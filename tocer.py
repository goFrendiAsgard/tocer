import re
import os
import sys
from typing import Tuple, Optional


def to_kebab(string: str) -> str:
    string = re.sub(r'[^a-zA-Z0-0\-]', ' ', string).strip()
    string = string.replace(' ', '-').strip()
    string = re.sub(r'(?<!^)(?=[A-Z])', '-', string).lower()
    string = re.sub(r'(-+)', '-', string).lower()
    return string


class LineChecker():
    def __init__(self, line: str):
        pattern = r'^(\s*)\* (.+)$'
        self.line_match: Optional[re.Match[str]] = re.match(pattern, line)

    def is_toc_item(self):
        return self.line_match is not None

    def get_components(self) -> Tuple[str, str]:
        '''
        Return a tuple.
        The first element of the tuple is the indentation.
        The second element of the tuple is the content of the TOC
        '''
        if self.line_match is None:
            return ('', '')
        return self.line_match.groups()


class LinkChecker():
    def __init__(self, content: str):
        pattern = r'\[(.+)]\((.+)\)'
        self.link_match: Optional[re.Match[str]] = re.match(pattern, content)

    def is_link(self):
        return self.link_match is not None

    def get_components(self) -> Tuple[str, str]:
        '''
        Return a tuple.
        The first element of the tuple is the caption
        The second element of the tuple is the doc_path
        '''
        if self.link_match is None:
            return ('', '')
        return self.link_match.groups()


class State():
    def __init__(self):
        self.indentations = []
        self.subdirs = []

    def get_path(self) -> str:
        if len(self.subdirs) == 0:
            return ''
        return os.path.join(*self.subdirs)

    def get_indentation(self) -> str:
        return ''.join(self.indentations)

    def is_leaf(self, current_indentation: str, next_line_checker: LineChecker) -> bool:
        if not next_line_checker.is_toc_item():
            return True
        next_line_indentation, _ = next_line_checker.get_components()
        if len(next_line_indentation) <= len(current_indentation):
            return True
        return False

    def get_level(self) -> int:
        return len(self.subdirs)

    def update(self, current_line_checker: LineChecker, current_link_checker: LinkChecker, next_line_checker: LineChecker):
        current_indentation, current_caption = current_line_checker.get_components()
        while len(current_indentation) < len(self.get_indentation()):
            self.indentations = self.indentations[:len(self.indentations)-1]
            self.subdirs = self.subdirs[:len(self.subdirs)-1]
        if self.is_leaf(current_indentation, next_line_checker):
            return
        if len(self.get_indentation()) == len(current_indentation) and len(self.indentations) > 0:
            # previous non-leaf item is on the same level, remove last element of the subdirs
            self.subdirs = self.subdirs[:len(self.subdirs)-1]
        else:
            # previous non-leaf item is on the top level, add new item
            new_indentation = current_indentation[len(self.get_indentation()):]
            self.indentations.append(new_indentation)
        # append to subdirs
        if current_link_checker.is_link():
            current_caption, _ =  current_link_checker.get_components()
        new_subdir = to_kebab(current_caption)
        self.subdirs.append(new_subdir)


def get_new_doc_path(toc_file_name: str, state: State, indentation: str, next_line_checker: LineChecker, caption: str) -> str:
    is_leaf = state.is_leaf(indentation, next_line_checker)
    path = state.get_path()
    if is_leaf:
        kebab_caption = to_kebab(caption)
        return os.path.join(path, '{kebab_caption}.md'.format(kebab_caption=kebab_caption))
    else:
        return os.path.join(path, toc_file_name)


def get_backlink_path(toc_file_name: str, level: int) -> str:
    if level == 0:
        return './{toc_file_name}'.format(toc_file_name=toc_file_name)
    backlink_parts = ['..'] * level
    backlink_parts.append(toc_file_name)
    return os.path.join(*backlink_parts)


def create_doc(toc_file_name: str, level: int, caption: str, doc_path: str):
    dirname = os.path.dirname(doc_path)
    if dirname != '' and not os.path.exists(dirname):
        os.makedirs(dirname)
    if not os.path.exists(doc_path):
        doc_file = open(doc_path, 'w')
        backlink_path = get_backlink_path(toc_file_name, level)
        doc_content = '\n'.join([
            '[⬅️ Table of Content]({backlink_path})'.format(backlink_path=backlink_path),
            '# {caption}'.format(caption=caption),
        ])
        doc_file.write(doc_content)


def main(toc_file_name: str):
    old_readme_file = open(toc_file_name, 'r')
    old_lines = old_readme_file.read().split('\n')
    state = State()
    new_lines = []
    for index, old_line in enumerate(old_lines):
        line_checker = LineChecker(old_line)
        if not line_checker.is_toc_item():
            new_lines.append(old_line)
            continue
        indentation, original_caption = line_checker.get_components()
        link_checker = LinkChecker(original_caption)
        next_line = old_lines[index+1] if index+1 < len(old_lines) else ''
        next_line_checker = LineChecker(next_line)
        state.update(line_checker, link_checker, next_line_checker)
        level = state.get_level()
        if link_checker.is_link():
            # already a link, don't touch this line
            new_lines.append(old_line)
            original_caption, doc_path = link_checker.get_components()
            create_doc(toc_file_name, level, original_caption, doc_path)
            continue
        new_doc_path = get_new_doc_path(toc_file_name, state, indentation, next_line_checker, original_caption)
        new_line = '{indentation}* [{caption}]({link})'.format(indentation=indentation, caption=original_caption, link=new_doc_path)
        create_doc(toc_file_name, level, original_caption, new_doc_path)
        new_lines.append(new_line)
    new_readme_file = open(toc_file_name, 'w')
    new_readme_file.write('\n'.join(new_lines))


if __name__ == '__main__':
    toc_file_name = sys.argv[1] if len(sys.argv) > 1 else 'README.md'
    main(toc_file_name)
