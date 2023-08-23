import sys, re, ast
from helpers import split_line, list_files, is_py

class CustomError(Exception):
    length = ('Error1', "Line too long")
    indentation = ('Error2', 'Indentation should be a multiple of four')
    semicolon = ('Error3', 'Redundant semicolon after a statement ')
    spaces = ('Error4', 'Inline comments should have atleast two spaces before inline comments')
    todo = ('Error5', 'Todo found')
    lines = ('Error6', 'Found more than two consecutive blank lines before a code line')
    construction_space = ('Error7', '')
    casing = ('Error8', '')
    function_name = ('Error9', '')
    arg = ('Error10', 'Argument names must be written in snake_case')
    var = ('Error11', 'Variables must be written in snake_case')
    default = ('Error12', 'A default argument value must not be mutable')

    def __init__(self, issue, line_num, other_message=None):
        self.message = f"{file_path}: Line {line_num}: {getattr(self, issue)[0]} {other_message if other_message else getattr(self, issue)[1]}"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ArgumentVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_FunctionDef(self, node):
        line_no = node.lineno
        fun_args = [a.arg for a in node.args.args]
        for arg in fun_args:
            if not arg.islower() and '_' not in arg:
                self.errors += [CustomError('arg', line_no).message]
        body_ = node.body
        item_line = 0
        for item in body_:  # to check local var names
            item_line += 1
            if isinstance(item, ast.Assign) and isinstance(item.targets[0], ast.Name):
                if '_' not in item.targets[0].id:
                    self.errors += [CustomError('var', line_no + item_line).message]
        for default in node.args.defaults:  # checks default args
            if not isinstance(default, ast.Constant):
                self.errors += [CustomError('default', line_no).message]
        self.generic_visit(node)

    def get_node_errors(self):
        return self.errors


def length_check(line, idx):
    if len(line) > 79:
        return CustomError('length', idx).message


def indentation_check(line, idx):
    if line != '\n' and (len(line) - len(line.lstrip())) % 4:
        return CustomError('indentation', idx).message


def semi_colon_check(statement, idx):
    section_1, section_2 = split_line(statement)
    if section_1.strip().endswith(';'):
        return CustomError('semicolon', idx).message


def space_check(statement, idx):
    section_1, section_2 = split_line(statement)
    if section_2 is not None and len(section_1) > 0 and not section_1.endswith('  '):
        return CustomError('spaces', idx).message


def check_construction(statement):
    """ checks space after construction name, def or class"""
    construction = None
    template = r'(class|def)(\s{2,})'
    if re.match(template, statement.strip()):
        if re.match('class', statement):
            construction = 'class'
        else:
            construction = 'def'
        return construction


def check_casing(statement):
    """class names should be in pascal case/camelcase"""
    if re.match('class', statement):
        class_name = statement.split(' ')[1].strip()
        if re.match('^[A-Z]', class_name) is None:
            return class_name.split(':')[0]


def check_function_name(statement):
    if re.match('def', statement):
        function_name = statement.split(' ')[1].strip()
        if not function_name.islower() and '_' not in function_name:
            return function_name


def todo_check(statement, idx):
    section_1, section_2 = split_line(statement)
    if section_2 is not None and 'todo' in section_2.lower():
        return CustomError('todo', idx).message


def ast_checks(file_content):
    tree = ast.parse(file_content)
    ast_ = ArgumentVisitor()
    ast_.visit(tree)
    return ast_.get_node_errors()


def file_checks(file):
    empty_lines = 0
    checks = []
    for idx, line_item in enumerate(file, start=1):
        construction_name_error = check_construction(line_item)
        class_case = check_casing(line_item)
        function_name = check_function_name(line_item.lstrip())
        if line_item == '\n':
            empty_lines += 1
            continue
        checks += [length_check(line_item, idx), indentation_check(line_item, idx), semi_colon_check(line_item, idx),
                  space_check(line_item, idx), todo_check(line_item, idx)]
        if empty_lines > 2:
            checks += [CustomError('lines', idx).message]
        empty_lines = 0
        if construction_name_error:
            checks += [CustomError('construction_space', idx,
                                   other_message=f"Too many spaces after '{construction_name_error}'").message]
        if class_case:
            checks += [CustomError('casing', idx,
                                   other_message=f"Class name '{class_case}' should be written in CamelCase").message]
        if function_name:
            checks += [CustomError('function_name', idx,
                                   other_message=f"Function name '{function_name}' should be written in snake_case").message]
    return [err for err in checks if err is not None]


if __name__ == '__main__':
    args = sys.argv
    input_path = args[1]
    file_path = ''
    all_errors = []
    for file_item in list_files(input_path):
        file_path = file_item
        if is_py(file_item):
            all_checks = []
            with open(file_item, 'r') as file_to_read:
                all_checks += file_checks(file_to_read.readlines())
            with open(file_item, 'r') as file_to_read:
                all_checks += ast_checks(file_to_read.read())
            for error in all_checks:
                print(error)


