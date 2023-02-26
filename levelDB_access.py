from openwpm.utilities.db_utils import get_content
from tqdm import tqdm
from pathlib import Path
from hashlib import sha512
from custom.File_Helper import list_files_in_path, open_json, del_files_in_path, dump_json, D_TMP

def check_levelDB(local_level_db, script):
    k_hash = None

    # list out keys and values separately
    key_list = list(local_level_db.keys())
    val_list = list(local_level_db.values())
    
    # print key with val script
    try:
        position = val_list.index(script)

        k_hash = key_list[position]

    except ValueError:
        None
    
    return k_hash

# Not used
def check_tmp_files(script):
    print("tmp_check")

    k_hash = None

    tmp_files = list_files_in_path(D_TMP)
    
    for f in tmp_files:
        print(f)
        tmp_levelDB = open_json(f, D_TMP)
        k_hash = check_levelDB(tmp_levelDB, script)

        if k_hash:
            break    

    return k_hash

def hash512(input):
    return sha512(input).hexdigest()
    #return sha256(input.encode('utf-8')).hexdigest()


# START
level_db_path = Path("./datadir/crawl-data-leveldb")

del_files_in_path(D_TMP)

cursor = get_content(level_db_path)

siblings_hash = {}
level_db = {}

print("Start Check...")
count = 0
for t_hash, t_script in tqdm(cursor):

    count += 1

    # Data is returned as bytes:  b'04c640b950f2cdeebe03e63961e4b4d945febf6737abc25ff1695233cc7af4ed'
    # decoding returns a string: 04c640b950f2cdeebe03e63961e4b4d945febf6737abc25ff1695233cc7af4ed
    t_hash = t_hash.decode("utf-8")
    
    # Hashing whole script on my own to better compare and process
    # t_script = str(t_script)
    t_s_hash = hash512(t_script)

    k_hash = check_levelDB(level_db, t_s_hash)
    
    """
    if not k_hash and count > 1000:
        k_hash = check_tmp_files(t_script)
    """
    
    if k_hash:
        if siblings_hash.get(k_hash):
            siblings_hash[k_hash].append(t_hash)
        else:
            siblings_hash[k_hash] = [t_hash]

    level_db[t_hash] = t_s_hash

    """
    if count % 1000 == 0:
        dump_json(level_db, "levelDB_{}.json".format(int(count/1000)), D_TMP)
        dump_json(siblings_hash, "sibling_hash.json", mode="a")
        level_db = {}
    """

dump_json(level_db, "levelDB_{}.json".format(count), D_TMP)
dump_json(siblings_hash, "sibling_hash.json", mode="a")

print("LevelDB elements: {}".format(len(level_db))) # 53273
print("Siblings: {}".format(len(siblings_hash))) # 7983