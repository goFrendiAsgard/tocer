from turtle import back
from typing import Any, List, Optional, TypeVar
import re
import os
import subprocess
import sys


def to_kebab(string: str) -> str:
    string = re.sub(r'[^a-zA-Z0-9\-]', ' ', string).strip()
    string = string.replace(' ', '-').strip()
    string = re.sub(r'(?<!^)(?=[A-Z])', '-', string).lower()
    string = re.sub(r'(-+)', '-', string).lower()
    return string

def create_start_tag(tag_name: str) -> str:
    return '<!--start{}-->'.format(tag_name.capitalize())

def create_end_tag(tag_name: str) -> str:
    return '<!--end{}-->'.format(tag_name.capitalize())

def is_match_start_tag(tag_name: str, line: str) -> bool:
    pattern = r'{}'.format(create_start_tag(tag_name))
    return re.match(pattern, line) is not None

def is_match_end_tag(tag_name: str, line: str) -> bool:
    pattern = r'{}'.format(create_end_tag(tag_name))
    return re.match(pattern, line) is not None

def replace_tag_content(tag_name: str, replacement_text: str, text: str) -> str:
    start_tag = create_start_tag(tag_name)
    end_tag = create_end_tag(tag_name)
    replacements = [start_tag, replacement_text, end_tag] if replacement_text != '' else [start_tag, end_tag]
    return re.sub(
        r'{start_tag}.*{end_tag}'.format(start_tag=start_tag, end_tag=end_tag), 
        '\n'.join(replacements), 
        text,
        flags=re.DOTALL
    )

def process_code_tag(text: str) -> str:
    start_tag = create_start_tag('code')
    end_tag = create_end_tag('code')
    code_delimiter='```'
    return re.sub(
        r'({start_tag})\s*{code_delimiter}([a-zA-Z0-9_\-]*)\s(.*)\s{code_delimiter}.*({end_tag})'.format(start_tag=start_tag, end_tag=end_tag, code_delimiter=code_delimiter), 
        _replace_code_tag_match,
        text,
        flags=re.DOTALL
    )

def _replace_code_tag_match(match_obj: Any) -> str:
    code_delimiter='```'
    start_tag, code_type, code, end_tag = match_obj.groups()
    output = subprocess.check_output(['bash', '-c', code]).decode('utf-8')
    return '\n'.join([
        start_tag,
        '{}{}'.format(code_delimiter, code_type).strip(),
        code.strip(),
        code_delimiter,
        '',
        code_delimiter,
        output,
        code_delimiter,
        end_tag
    ])


TNode = TypeVar('TNode', bound='Node')
class Node():

    def __init__(self, line_index: int, line: str, toc_file_name: str):
        self.parent: Optional[Node] = None
        self.children: List[Node] = []
        self.line_index = line_index
        self.line = line
        self.toc_file_name = toc_file_name
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
        self._parse_doc()
        for child in self.children:
            child.adjust_doc()
 
    def _create_doc(self):
        new_link = self.get_new_link()
        dirname = os.path.dirname(new_link)
        if dirname != '' and not os.path.exists(dirname):
            os.makedirs(dirname)
        if self.old_link != new_link and os.path.exists(self.old_link):
            os.rename(self.old_link, new_link)
        if os.path.exists(new_link):
            return
        doc_file = open(new_link, 'w')
        doc_content = '\n'.join([
            create_start_tag('tocHeader'),
            create_end_tag('tocHeader'),
            '',
            'TODO: Write about `{}`'.format(self.caption),
            '',
            create_start_tag('tocSubtopic'),
            create_end_tag('tocSubtopic'),
        ])
        doc_content = process_code_tag(doc_content)
        doc_file.write(doc_content)

    def _parse_doc(self):
        link = self.get_new_link()
        old_doc_file = open(link, 'r')
        content = old_doc_file.read()
        content = replace_tag_content('tocHeader', self._get_header(), content)
        content = replace_tag_content('tocSubtopic', self._get_subtopic(), content)
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

    def __init__(self, toc_file_name: str, old_lines: List[str]):
        self.toc_file_name = toc_file_name
        self.root = Node(-1, '', toc_file_name)
        self.current = self.root
        self.old_lines = old_lines
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
            new_node = Node(line_index, line, self.toc_file_name)
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


def main(toc_file_name: str):
    old_readme_file = open(toc_file_name, 'r')
    old_lines = old_readme_file.read().split('\n')
    tree = Tree(toc_file_name, old_lines)
    new_lines = tree.replace_lines()
    tree.adjust_doc()
    new_content = process_code_tag('\n'.join(new_lines))
    new_readme_file = open(toc_file_name, 'w')
    new_readme_file.write(new_content)

if __name__ == '__main__':
    toc_file_name = sys.argv[1] if len(sys.argv) > 1 else 'README.md'
    main(toc_file_name)