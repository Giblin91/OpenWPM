# CUSTOM CALO
import os
import csv
from pathlib import Path

# Assumes is in OpenWP/custom/
ROOT: Path = Path(__file__).parent.parent.absolute()
PATH_TO_COOKIES = ROOT / "custom/src/accept_cookies.txt"
PATH_TO_TRANCO = ROOT / "custom/src/tranco_10k.csv"
PATH_TO_DCFP_HTML = ROOT / "custom/src/DeviceClassFP.html"

def check_file_in_path(file_name, file_path):

    if not os.path.exists(file_path):
        os.mkdir(file_path)
        raise Exception(f"Path \'{file_path}\' does not exist, check failed for file \'{file_name}\'")
    
    return os.path.exists(file_path / file_name)

# Dump list to specified file name in default OpenWPM/datadir
def dump_list(list, file_name, path = ROOT / "datadir", mode = "w"):

    if mode == "a" and not check_file_in_path(file_name, path):
        mode = "w"

    dump = ""
    for element in list:
        dump += "{}\n".format(element)

    with open(path / file_name, mode) as log:
        log.write(dump)

def get_tranco_domains(count=None):

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
