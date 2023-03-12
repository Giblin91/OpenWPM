from openwpm.utilities.db_utils import get_content
from tqdm import tqdm
from custom.File_Helper import dump_json, hash_sha256, hash_sha512, LEVELDB, D_EXTRACT
import shutil
import os

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

    file_name = "extracted_levelDB.json"
    dump_json(level_db, file_name, D_EXTRACT)

    print("LevelDB elements: {}".format(len(level_db)))

    return file_name

def copy_to_DeviceClassCrawl(file_name : str):
    path = "/home/lor/Projects/DeviceClassCrawl/OpenWPM/datadir"
    
    src = D_EXTRACT / file_name
    dst = path + "/" + file_name

    print(f"Before copying\n{os.listdir(path)}")
    
    if os.path.exists(dst):
        os.remove(dst)
    print(shutil.copyfile(src, dst))
    
    print(f"After copying\n{os.listdir(path)}")

def main():

    print("Prepare for extraction...")

    # Make a clean extraction
    # TODO not needed? I overwite existing file
    #del_files_in_path(D_EXTRACT)

    file_name = level_db_to_json()

    copy_to_DeviceClassCrawl(file_name)

    #t.log("Some msg")
    #Zip or compress sql...? and move it to extract? Move it and then compress all?

if __name__ == "__main__":
    main()