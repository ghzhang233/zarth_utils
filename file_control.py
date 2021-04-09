import os

path_run = os.getcwd()
path_code = os.path.abspath(os.path.dirname(__file__))


def get_all_files(path=path_run):
    g = os.listdir(path)
    for filename in g:
        if not os.path.isdir(filename):
            print(filename)
