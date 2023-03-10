from openwpm.utilities.db_utils import get_content
from tqdm import tqdm
from hashlib import sha256
from custom.File_Helper import dump_json, LEVELDB, D_EXTRACT
import custom.Time as t


def hash_sha256(input):
    return sha256(input).hexdigest()
    #return sha256(input.encode('utf-8')).hexdigest()

def level_db_to_json():

    cursor = get_content(LEVELDB)

    level_db = {}

    print("LevelDB Extraction...")
    count = 0
    for key_hash, script in tqdm(cursor):

        count += 1

        # Data is returned as bytes:  b'04c640b950f2cdeebe03e63961e4b4d945febf6737abc25ff1695233cc7af4ed'
        # decoding returns a string: 04c640b950f2cdeebe03e63961e4b4d945febf6737abc25ff1695233cc7af4ed
        key_hash = key_hash.decode("utf-8")
        
        # Hashing whole script on my own to better compare and process
        # script = str(script)
        sha_hash = hash_sha256(script)
        level_db[key_hash] = sha_hash

    dump_json(level_db, "levelDB_{}.json".format(count), D_EXTRACT)

    print("LevelDB elements: {}".format(len(level_db)))

def main():

    # Make a clean extraction
    # TODO not needed? I overwite existing file
    #del_files_in_path(D_EXTRACT)

    level_db_to_json()

    #t.log("Some msg")
    #Zip or compress sql...? and move it to extract? Move it and then compress all?

if __name__ == "__main__":
    main()