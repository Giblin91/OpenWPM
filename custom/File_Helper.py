# CUSTOM CALO
import os
import shutil
import csv
import json
from pathlib import Path
import logging
from hashlib import sha256, sha512

FILE_FORM = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
CONS_FORM = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Assumes is in OpenWP/custom/
ROOT: Path = Path(__file__).parent.parent.absolute()
PATH_TO_COOKIES = ROOT / "custom/src/accept_cookies.txt"
PATH_TO_TRANCO = ROOT / "custom/src/tranco_10k.csv"
PATH_TO_DCFP_HTML = ROOT / "custom/src/DeviceClassFP.html"
DATADIR = ROOT / "datadir"
D_TMP = DATADIR / "tmp"
D_EXTRACT = DATADIR / "extract"
OWPM_LOG = DATADIR / "openwpm.log"
SQLITE = DATADIR / "crawl-data.sqlite"
LEVELDB = DATADIR / "crawl-data-leveldb"
DCFP_LOG = D_EXTRACT / "crawl_dcfp.log"

def check_create_dir(file_path) -> bool:
    if not os.path.exists(file_path):
        os.mkdir(file_path)
        return False
    
    return True

def check_remove_dir(file_path) -> bool:
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
        return True
    return False

def check_file_in_path(file_name, file_path) -> bool:

    if not os.path.exists(file_path):
        raise Exception(f"Path \'{file_path}\' does not exist, check failed for file \'{file_name}\'")
    
    return os.path.exists(file_path / file_name)

def check_remove_file(file_path) -> bool:
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

# Dump list to specified file name in default OpenWPM/datadir
def dump_list(list, file_name, path = DATADIR, mode = "w"):

    if mode == "a" and not check_file_in_path(file_name, path):
        mode = "w"

    dump = ""
    for element in list:
        dump += "{}\n".format(element)

    with open(path / file_name, mode) as log:
        log.write(dump)

def open_json(file_name, path) -> (dict | None):
    data = None

    with open(path / file_name) as json_file:
        data = json.load(json_file)
    
    return data

# Dump list to specified file name in default OpenWPM/datadir
def dump_json(dict, file_name, path = DATADIR, mode = "w"):

    data = dict
    if mode == "a":
        if check_file_in_path(file_name, path):
            # This does not affect the other two dictionaries. ** implies that an argument is a dictionary.
            # Duplicates keys will be overwitten by the second.
            # Here we assume their keys are distinct
            data = {**open_json(file_name, path), **dict}
        
    # Replace if already existing
    out_file = open(path / file_name, "w")
    json.dump(data, out_file, indent = 4)
    out_file.close()

def get_tranco_domains(count=None) -> list[str]:

    domains = []

    # opening the CSV file
    with open(PATH_TO_TRANCO, mode ='r') as file:

        # reading the CSV file
        csvFile = csv.reader(file)

        # displaying the contents of the CSV file
        for i, line in enumerate(csvFile):
            domains.append("https://{}".format(line[1]))

            # Get only "count" of lines
            if i+1 == count:
                break
    
    return domains

def list_files_in_path(file_path) -> list[str]:

    files = []
    if not os.path.exists(file_path):
        print(f"Path \'{file_path}\' does not exist")
        return files

    # Lists ALL content of path
    all = os.listdir(file_path)

    for f in all:
        if os.path.isfile(file_path / f):
            files.append(f)

    return files

def del_files_in_path(file_path, files = None):

    if not os.path.exists(file_path):
        print(f"Path \'{file_path}\' does not exist")
        return
    
    if not files:
        files = list_files_in_path(file_path)
        
    for f in files:
        os.remove(file_path / f)

# To setup as many loggers as you want
def setup_logger(name = "CRAWL_DCFP", log_file = DCFP_LOG, level=logging.INFO, console=True) -> logging.Logger:

    # https://docs.python.org/3/howto/logging.html#handlers
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(FILE_FORM)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CONS_FORM)
        logger.addHandler(console_handler)

    return logger

def get_dcfp_logger(setup = False) -> logging.Logger:

    if setup:
        setup_logger()
    
    return logging.getLogger("CRAWL_DCFP")


def hash_sha256(input) -> str:
    return sha256(input).hexdigest()
    #return sha256(input.encode('utf-8')).hexdigest()

def hash_sha512(input) -> str:
    return sha512(input).hexdigest()