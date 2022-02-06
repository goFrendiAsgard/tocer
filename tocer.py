from typing import Tuple, Optional
import re
import os
import sys


def to_kebab(string: str) -> str:
    string = re.sub(r'[^a-zA-Z0-9\-]', ' ', string).strip()
    string = string.replace(' ', '-').strip()
    string = re.sub(r'(?<!^)(?=[A-Z])', '-', string).lower()
    string = re.sub(r'(-+)', '-', string).lower()
    return string


class LineChecker():
    def __init__(self, line: str):
        self.line = line
        line_pattern = r'^(\s*)\* (.+)$'
        self.line_match: Optional[re.Match[str]] = re.match(line_pattern, line)
        link_paattern = r'(\s*)\* \[(.+)]\((.+)\)'
        self.link_match: Optional[re.Match[str]] = re.match(link_paattern, line)
    
    def get_line(self) -> str:
        return self.line

    def is_toc_item(self) -> bool:
        return self.line_match is not None

    def is_link(self) -> bool:
        return self.link_match is not None

    def get_components(self) -> Tuple[str, str, str]:
        '''
        Return a tuple.
        The first element of the tuple is the indentation.
        The second element of the tuple is the caption
        The last element of the tuple is the url
        '''
        if self.line_match is None:
            return ('', '', '')
        if self.link_match is None:
            indentation, caption = self.line_match.groups()
            return (indentation, caption, '')
        return self.link_match.groups()


class State():
    def __init__(self):
        self.previous_indentations = []
        self.previous_subdirs = []
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
        next_line_indentation, _, _ = next_line_checker.get_components()
        if len(next_line_indentation) <= len(current_indentation):
            return True
        return False

    def get_level(self) -> int:
        return len(self.subdirs)

    def update(self, current_line_checker: LineChecker, next_line_checker: LineChecker):
        self.previous_indentations = self.indentations
        self.previous_subdirs = self.subdirs
        current_indentation, current_caption, _ = current_line_checker.get_components()
        while len(current_indentation) < len(self.get_indentation()):
            self.indentations = self.indentations[:len(self.indentations)-1]
            self.subdirs = self.subdirs[:len(self.subdirs)-1]
        # current is leaf
        if self.is_leaf(current_indentation, next_line_checker) and len(current_indentation) >= len(''.join(self.previous_indentations)):
            return
        if len(self.get_indentation()) == len(current_indentation) and len(self.indentations) > 0:
            # previous item is on the same level, remove last element of the subdirs
            self.subdirs = self.subdirs[:len(self.subdirs)-1]
        else :
            # previous item is on the top level, add new item
            new_indentation = current_indentation[len(self.get_indentation()):]
            self.indentations.append(new_indentation)
        # append to subdirs
        if not self.is_leaf(current_indentation, next_line_checker):
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
        indentation, caption, link = line_checker.get_components()
        next_line = old_lines[index+1] if index+1 < len(old_lines) else ''
        next_line_checker = LineChecker(next_line)
        state.update(line_checker, next_line_checker)
        level = state.get_level()
        if line_checker.is_link():
            # already a link, don't touch this line
            new_lines.append(old_line)
            create_doc(toc_file_name, level, caption, link)
            continue
        new_doc_path = get_new_doc_path(toc_file_name, state, indentation, next_line_checker, caption)
        new_line = '{indentation}* [{caption}]({link})'.format(indentation=indentation, caption=caption, link=new_doc_path)
        create_doc(toc_file_name, level, caption, new_doc_path)
        new_lines.append(new_line)
    new_readme_file = open(toc_file_name, 'w')
    new_readme_file.write('\n'.join(new_lines))


if __name__ == '__main__':
    toc_file_name = sys.argv[1] if len(sys.argv) > 1 else 'README.md'
    main(toc_file_name)
