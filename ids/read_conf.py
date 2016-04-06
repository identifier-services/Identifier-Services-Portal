from os.path import abspath, dirname, join, join, isdir, isfile
from os import listdir
import yaml


BASE_DIR = dirname(dirname(abspath(__file__)))
DESCRIPTIONS_DIR = join(BASE_DIR, 'conf/obj_descriptions')


def process(path):
    """ """
    files = [f for f in listdir(path) if isfile(join(path, f))]
    descriptions = {}
    for description in files:
        with open(join(path, description)) as f:
            data = yaml.safe_load(f)
        descriptions[description] = data
    return descriptions


def read(location=None):
    """ """
    if not location:
        location = DESCRIPTIONS_DIR

    dirs = [d for d in listdir(location) if isdir(join(location, d))]

    descriptions = {}

    for directory in dirs:
        descriptions[directory] = process(join(join(location, directory)))

    return descriptions


if __name__ == '__main__':
    print read()
