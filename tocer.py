# coding=utf8
from turtle import back
from typing import Any, List, Optional, TypeVar
import re
import os
import subprocess
import sys


def to_kebab(value: str) -> str:
    value = re.sub(r'[^a-zA-Z0-9\-]', ' ', value).strip()
    value = "-".join(value.lower().split())
    return value

def to_capital_first_letter(value: str) -> str:
    return re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), value, 1)

def create_start_tag(tag_name: str) -> str:
    return '<!--start{}-->'.format(to_capital_first_letter(tag_name))

def create_end_tag(tag_name: str) -> str:
    return '<!--end{}-->'.format(to_capital_first_letter(tag_name))

def is_match_start_tag(tag_name: str, line: str) -> bool:
    pattern = r'{}'.format(create_start_tag(tag_name))
    return re.match(pattern, line) is not None

def is_match_end_tag(tag_name: str, line: str) -> bool:
    pattern = r'{}'.format(create_end_tag(tag_name))
    return re.match(pattern, line) is not None

def remove_terminal_decorations(text: str) -> str:
    # https://www2.ccs.neu.edu/research/gpc/VonaUtils/vona/terminal/vtansi.htm
    result = re.sub(r".*[\n\r]\x1b\[1A*", "", text, flags=re.MULTILINE)
    result = re.sub(r".*\x1b\[2K[\r\n]", "", result, flags=re.MULTILINE)
    result = re.sub(r"\x1b\[[\?*[0-9]+[a-zA-Z]", "", result)
    return result

def replace_tag_content(tag_name: str, replacement_text: str, text: str) -> str:
    start_tag = create_start_tag(tag_name)
    end_tag = create_end_tag(tag_name)
    replacements = [start_tag, replacement_text, end_tag] if replacement_text.strip() != '' else [start_tag, end_tag]
    return re.sub(
        r'{start_tag}.*?{end_tag}'.format(start_tag=start_tag, end_tag=end_tag), 
        '\n'.join(replacements), 
        text,
        flags=re.DOTALL
    )

def process_code_tag(text: str, preprocess_code_script: str) -> str:
    start_tag = create_start_tag('code')
    end_tag = create_end_tag('code')
    return re.sub(
        r'{start_tag}(.*?){end_tag}'.format(start_tag=start_tag, end_tag=end_tag), 
        _create_replace_code_tag_match(preprocess_code_script, start_tag, end_tag),
        text,
        flags=re.DOTALL
    )

def _create_replace_code_tag_match(preprocess_code_script: str, start_tag: str, end_tag: str):
    def _replace_code_tag_match(match_obj: Any) -> str:
        code_delimiter='```'
        output_delimiter='```````'
        content = match_obj.groups()[0]
        content_matches = re.match(
            r'.*?{code_delimiter}([a-zA-Z0-9_\-]*?)\s(.*?)\s{code_delimiter}.*'.format(code_delimiter=code_delimiter),
            content,
            flags=re.DOTALL
        )
        code_type, code = content_matches.groups()
        script = '\n'.join([preprocess_code_script, code])
        print('Processing code: {script}'.format(script=script))
        raw_output = subprocess.check_output(['bash', '-c', script], stderr=subprocess.STDOUT).decode('utf-8')
        output = remove_terminal_decorations(raw_output)
        print('Getting output: {output}'.format(output=output))
        return '\n'.join([
            start_tag,
            '{}{}'.format(code_delimiter, code_type).strip(),
            code.strip(),
            code_delimiter.strip(),
            ' ',
            '<details>',
            '<summary>Output</summary>',
            ' ',
            output_delimiter.strip(),
            output.strip(),
            output_delimiter.strip(),
            '</details>',
            end_tag
        ])
    return _replace_code_tag_match 


TNode = TypeVar('TNode', bound='Node')
class Node():

    def __init__(self, line_index: int, line: str, toc_file_name: str, preprocess_code_script: str):
        self.parent: Optional[Node] = None
        self.children: List[Node] = []
        self.line_index = line_index
        self.line = line
        self.toc_file_name = toc_file_name
        self.preprocess_code_script = preprocess_code_script
        self.indentation = ''
        self.caption = '🏠'
        self.old_link = ''
        item_pattern = r'^(\s*)\* (.+)$'
        self.item_match: Optional[re.Match[str]] = re.match(item_pattern, line)
        link_pattern = r'(\s*)\* \[(.+)]\((.+)\)'
        self.link_match: Optional[re.Match[str]] = re.match(link_pattern, line)
        self._populate_line_properties()

    def _populate_line_properties(self): 
        if self.is_link():
            self.indentation, self.caption, self.old_link = self.link_match.groups()
            return
        if self.is_item():
            self.indentation, self.caption = self.item_match.groups()

    def is_item(self) -> bool:
        return self.item_match is not None

    def is_link(self) -> bool:
        return self.link_match is not None

    def is_root(self) -> bool:
        return self.parent is None

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def add_child(self, other_node: TNode):
        self.children.append(other_node)
        other_node.parent = self

    def get_indentation_count(self) -> int:
        return len(self.indentation)

    def get_new_link(self) -> str:
        links = []
        cursor = self
        while not cursor.is_root():
            links.insert(0, to_kebab(cursor.caption))
            cursor = cursor.parent
        link_prefix = ''
        if len(links) > 0:
            link_prefix = os.path.join(*links)
        if self.is_leaf():
            return link_prefix + '.md'
        return os.path.join(link_prefix, self.toc_file_name)

    def get_new_relative_link(self, start: str):
        link = self.get_new_link()
        return os.path.relpath(link, start)

    def get_new_line(self) -> str:
        return '{}* [{}]({})'.format(self.indentation, self.caption, self.get_new_link())

    def print(self):
        print('Line Index: {}, New Line:{}'.format(self.line_index, self.get_new_line()))
        for child in self.children:
            child.print()

    def replace_lines(self, lines: List[str]) -> List[str]:
        line_index = self.line_index
        if line_index >= 0:
            new_line = self.get_new_line()
            lines[line_index] = new_line
        for child in self.children:
            lines = child.replace_lines(lines)
        return lines 

    def adjust_doc(self):
        self._create_doc()
        for child in self.children:
            child.adjust_doc()
        print('Parsing {link}'.format(link=self.get_new_link()))
        self._parse_doc()
        print('Done parsing {link}'.format(link=self.get_new_link()))

    def _create_doc(self):
        new_link = self.get_new_link()
        dirname = os.path.dirname(new_link)
        if dirname != '' and not os.path.exists(dirname):
            print('Making directory {dirname}'.format(dirname=dirname))
            os.makedirs(dirname)
        if self.old_link != new_link and os.path.exists(self.old_link):
            print('Renaming {old_link} to {new_link}'.format(old_link=self.old_link, new_link=new_link))
            os.rename(self.old_link, new_link)
        if os.path.exists(new_link):
            return
        print('Creating {link}'.format(link=self.get_new_link()))
        doc_file = open(new_link, 'w')
        doc_content = '\n'.join([
            create_start_tag('tocHeader'),
            create_end_tag('tocHeader'),
            '',
            'TODO: Write about `{}`'.format(self.caption),
            '',
            create_start_tag('TocSubTopic'),
            create_end_tag('TocSubTopic'),
        ])
        doc_file.write(doc_content)
        print('Done creating {link}'.format(link=self.get_new_link()))

    def _parse_doc(self):
        link = self.get_new_link()
        old_doc_file = open(link, 'r')
        content = old_doc_file.read()
        print('Processing TOC header tag')
        content = replace_tag_content('tocHeader', self._get_header(), content)
        print('Processing TOC subtopic tag')
        content = replace_tag_content('TocSubTopic', self._get_subtopic(), content)
        print('Processing code tag')
        content = process_code_tag(content, self.preprocess_code_script)
        print('Done processing code tag')
        new_doc_file = open(link, 'w')
        new_doc_file.write(content)

    def _get_header(self) -> str:
        return '\n'.join([
            self._get_breadcrumb(),
            '# {}'.format(self.caption),
        ])

    def _get_breadcrumb(self) -> str:
        if self.is_root():
            return ''
        breadcrumb_list = []
        initial_backlink = self.toc_file_name if self.is_leaf() else os.path.join(*['..', self.toc_file_name])
        backlink_parts = [initial_backlink]
        cursor = self.parent
        while cursor is not None:
            backlink = os.path.join(*backlink_parts)
            breadcrumb = '[{}]({})'.format(cursor.caption, backlink)
            breadcrumb_list.insert(0, breadcrumb)
            cursor = cursor.parent
            backlink_parts.insert(0, '..')
        return ' > '.join(breadcrumb_list)

    def _get_subtopic(self) -> str:
        current_dir = os.path.dirname(self.get_new_link())
        subtopic_list = self._get_subtopic_list('', current_dir)
        if len(subtopic_list) == 0:
            return ''
        else:
            return '\n'.join([
                '# Sub-topics',
                '\n'.join(subtopic_list)
            ])

    def _get_subtopic_list(self, indentation:str, current_dir:str) -> List[str]:
        subtopic_list = []
        for child in self.children:
            subtopic_list.append('{}* [{}]({})'.format(indentation, child.caption, child.get_new_relative_link(current_dir)))
            subtopic_list += child._get_subtopic_list(indentation+'  ', current_dir)
        return subtopic_list


class Tree():

    def __init__(self, toc_file_name: str, old_lines: List[str], preprocess_code_script: str):
        self.toc_file_name = toc_file_name
        self.root = Node(-1, '', toc_file_name, preprocess_code_script)
        self.current = self.root
        self.old_lines = old_lines
        self.preprocess_code_script = preprocess_code_script
        self._parse_old_lines()

    def _parse_old_lines(self):
        should_parse_toc = False
        for line_index, line in enumerate(self.old_lines):
            if is_match_start_tag('toc', line):
                should_parse_toc = True
            elif is_match_end_tag('toc', line):
                should_parse_toc = False
            if not should_parse_toc:
                continue
            new_node = Node(line_index, line, self.toc_file_name, self.preprocess_code_script)
            if not new_node.is_item():
                continue
            if self.current.is_root():
                self.current.add_child(new_node)
                self.current = new_node
                continue
            while not self.current.is_root() and self.current.get_indentation_count() >= new_node.get_indentation_count():
                self.current = self.current.parent
            self.current.add_child(new_node)
            self.current = new_node

    def print(self):
        return self.root.print()

    def replace_lines(self) -> List[str]:
        new_lines = list(self.old_lines)
        return self.root.replace_lines(new_lines)

    def adjust_doc(self):
        self.root.adjust_doc()


def main(toc_file_name: str, preprocess_code_script: str):
    old_readme_file = open(toc_file_name, 'r')
    old_lines = old_readme_file.read().split('\n')
    tree = Tree(toc_file_name, old_lines, preprocess_code_script)
    new_lines = tree.replace_lines()
    tree.adjust_doc()
    new_content = process_code_tag('\n'.join(new_lines), preprocess_code_script)
    new_readme_file = open(toc_file_name, 'w')
    new_readme_file.write(new_content)

if __name__ == '__main__':
    toc_file_name = sys.argv[1] if len(sys.argv) > 1 else 'README.md'
    preprocess_code_script = sys.argv[2] if len(sys.argv) > 2 else 'if [ -f "~/.bashrc" ]; then source "~/.bashrc"; fi;'
    main(toc_file_name, preprocess_code_script)