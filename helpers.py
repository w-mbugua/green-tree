import os


def split_line(line):
    new_line = line.split('#')
    a, b = None, None
    if len(new_line) > 1:
        a, b = new_line[0], new_line[1]
    else:
        a = line
    return a, b


def is_py(file):
    return os.path.basename(file).endswith('.py')


def extract_folder(path):
    contents = []
    for item in os.listdir(path):
        if os.path.isfile(item):
            contents.append(os.path.join(path, item))
    return contents


def list_files(path):
    if os.path.isfile(path):
        return [path]
    if os.path.isdir(path):
        contents = []
        for item in os.listdir(path):
            item = os.path.join(path, item)
            if os.path.isfile(item):
                contents.append(item)
            elif os.path.isdir(item):
                contents.extend(extract_folder(item))
        return sorted(contents, key=os.path.basename)


def get_line(err_msg):
    if err_msg is not None:
        parts = err_msg.split(':')
        return int(parts[1].strip().split(' ')[1])


def get_code(err_msg):
    if err_msg is not None:
        parts = err_msg.split(':')
        return parts[2].strip().split(' ')[0]

