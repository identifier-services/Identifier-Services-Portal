from os.path import abspath, dirname, join, join, isdir, isfile
from os import listdir
import yaml, pprint


BASE_DIR = dirname(dirname(abspath(__file__)))
DESCRIPTIONS_DIR = join(BASE_DIR, 'conf/obj_descriptions')


def process_file(path, conf_file):
    """ """
    with open(join(path, conf_file)) as f:
        data = yaml.safe_load(f)
    key = conf_file.split('.')[0]
    return { key : data }


def process_dir(path):
    """ """
    files = [f for f in listdir(path) if isfile(join(path, f))]

    descriptions = {}
    for conf_file in files:
        descriptions.update(process_file(path, conf_file))

    return descriptions


def read(location=None):
    """ """
    if not location:
        location = DESCRIPTIONS_DIR

    dirs = [d for d in listdir(location) if isdir(join(location, d))]

    descriptions = {}

    for directory in dirs:
        descriptions[directory] = process_dir(join(join(location, directory)))

    files = [f for f in listdir(location) if isfile(join(location, f))]

    for conf_file in files:
        descriptions.update(process_file(location, conf_file))

    return descriptions


if __name__ == '__main__':
    pprint.pprint(read())
