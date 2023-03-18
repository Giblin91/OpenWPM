from openwpm.utilities.db_utils import get_content
from tqdm import tqdm
from custom.File_Helper import dump_json, hash_sha512, LEVELDB, D_EXTRACT, EXT_LVLDB, SQLITE, SQL_BZ2, OWPM_LOG, OWP_NAME
import shutil
import os
import bz2

# TODO I could do a sqlite query to extract only http_header hashes for js url of Canvas API to reduce extraction time and size
# look at SELECT_JS_HTTP_URL in db_extract_v3

def level_db_to_json():

    print("Get Level DB")

    level_db = {}
    cursor = get_content(LEVELDB)

    print("LevelDB Extraction...")
    for key_hash, script in tqdm(cursor):

        # Data is returned as bytes:  b'04c640b950f2cdeebe03e63961e4b4d945febf6737abc25ff1695233cc7af4ed'
        # decoding returns a string: 04c640b950f2cdeebe03e63961e4b4d945febf6737abc25ff1695233cc7af4ed
        key_hash = key_hash.decode("utf-8")
        
        # Hashing whole script on my own to better compare and process
        # script = str(script)
        #sha_hash = hash_sha256(script)
        sha_hash = hash_sha512(script)
        level_db[key_hash] = sha_hash

    dump_json(level_db, EXT_LVLDB, D_EXTRACT)

    print("LevelDB elements: {}".format(len(level_db)))

def copy_to_DeviceClassCrawl():
    path = "/home/lor/Projects/DeviceClassCrawl/OpenWPM/datadir"
    
    src = D_EXTRACT / EXT_LVLDB
    dst = path + "/" + EXT_LVLDB

    print(f"Before copying\n{os.listdir(path)}")
    
    if os.path.exists(dst):
        os.remove(dst)
    print(shutil.copyfile(src, dst))
    
    print(f"After copying\n{os.listdir(path)}")

def compress_sqlite():
    print("Compressing Sqlite...")

    filename_in = SQLITE
    filename_out = D_EXTRACT / SQL_BZ2

    with open(filename_in, mode="rb") as fin, bz2.open(filename_out, "wb") as fout:
        fout.write(fin.read())

    print(f"Uncompressed size: {os.stat(filename_in).st_size}")
    # Uncompressed size: 1000000
    print(f"Compressed size: {os.stat(filename_out).st_size}")


def copy_file(src, dst):
    print("Copying file...")
    print(f"SRC: {src}")
    print(f"DST: {dst}")

    if os.path.exists(dst):
        os.remove(dst)

    shutil.copyfile(src, dst)


def main():

    print("Prepare for extraction...")

    level_db_to_json()

    #copy_to_DeviceClassCrawl()

    #t.log("Some msg")
    #compress_sqlite()
    #Zip or compress sql...? and move it to extract? Move it and then compress all?
    # TODO extract needed queries as txt of tuples?

    #copy_file(OWPM_LOG, D_EXTRACT / OWP_NAME)

if __name__ == "__main__":
    main()