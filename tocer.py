from turtle import back
from typing import List, Optional, TypeVar
import re
import os
import sys


def to_kebab(string: str) -> str:
    string = re.sub(r'[^a-zA-Z0-9\-]', ' ', string).strip()
    string = string.replace(' ', '-').strip()
    string = re.sub(r'(?<!^)(?=[A-Z])', '-', string).lower()
    string = re.sub(r'(-+)', '-', string).lower()
    return string

def is_match_tag(tag: str, line: str) -> bool:
    pattern = r'<!--{}-->'.format(tag)
    return re.match(pattern, line) is not None

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
        self.link = ''
        item_pattern = r'^(\s*)\* (.+)$'
        self.item_match: Optional[re.Match[str]] = re.match(item_pattern, line)
        link_pattern = r'(\s*)\* \[(.+)]\((.+)\)'
        self.link_match: Optional[re.Match[str]] = re.match(link_pattern, line)
        self._populate_line_properties()

    def _populate_line_properties(self): 
        if self.is_link():
            self.indentation, self.caption, self.link = self.link_match.groups()
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

    def get_link(self) -> str:
        if self.link:
            return self.link
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

    def get_relative_link(self, start: str):
        link = self.get_link()
        return os.path.relpath(link, start)

    def get_new_line(self) -> str:
        if self.is_link():
            return self.line
        return '{}* [{}]({})'.format(self.indentation, self.caption, self.get_link())

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
        link = self.get_link()
        dirname = os.path.dirname(link)
        if dirname != '' and not os.path.exists(dirname):
            os.makedirs(dirname)
        if os.path.exists(link):
            return
        doc_file = open(link, 'w')
        doc_content = '\n'.join([
            '<!--startTocHeader-->',
            '<!--endTocHeader-->',
            'TODO: Write about `{}`'.format(self.caption),
            '<!--startTocSubtopic-->',
            '<!--endTocSubtopic-->',
        ])
        doc_file.write(doc_content)

    def _parse_doc(self):
        link = self.get_link()
        old_doc_file = open(link, 'r')
        content = old_doc_file.read()
        # replace tocHeader
        content = re.sub(
            r'<!--startTocHeader-->.*<!--endTocHeader-->', 
            '\n'.join([
                '<!--startTocHeader-->',
                self._get_breadcrumb(),
                '# {}'.format(self.caption),
                '<!--endTocHeader-->',
            ]), 
            content,
            flags=re.DOTALL
        )
        # replace tocSubtopic
        content = re.sub(
            r'<!--startTocSubtopic-->.*<!--endTocSubtopic-->', 
            '\n'.join([
                '<!--startTocSubtopic-->',
                self._get_subtopic(),
                '<!--endTocSubtopic-->',
            ]), 
            content,
            flags=re.DOTALL
        )
        new_doc_file = open(link, 'w')
        new_doc_file.write(content)

    def _get_subtopic(self) -> str:
        current_dir = os.path.dirname(self.get_link())
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
            subtopic_list.append('{}* [{}]({})'.format(indentation, child.caption, child.get_relative_link(current_dir)))
            subtopic_list += child._get_subtopic_list(indentation+'  ', current_dir)
        return subtopic_list

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
            if is_match_tag('startToc', line):
                should_parse_toc = True
            elif is_match_tag('endToc', line):
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

    def create_doc(self):
        self.root.adjust_doc()


def main(toc_file_name: str):
    old_readme_file = open(toc_file_name, 'r')
    old_lines = old_readme_file.read().split('\n')
    tree = Tree(toc_file_name, old_lines)
    new_lines = tree.replace_lines()
    tree.create_doc()
    new_readme_file = open(toc_file_name, 'w')
    new_readme_file.write('\n'.join(new_lines))

if __name__ == '__main__':
    toc_file_name = sys.argv[1] if len(sys.argv) > 1 else 'README.md'
    main(toc_file_name)
