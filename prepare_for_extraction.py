from openwpm.utilities.db_utils import get_content
from tqdm import tqdm
import time
from custom.File_Helper import (open_file, dump_json, hash_sha512, get_from_db,
                                LEVELDB, D_EXTRACT, EXT_LVLDB, SQLITE, SQL_BZ2, OWPM_LOG, OWP_LOG_NAME, DCFP_LOG, DCFP_LOG_NAME)
import shutil
import os
import bz2

INC_VISITS = "SELECT DISTINCT i.visit_id FROM incomplete_visits AS i;"
SITE_VISITS = "SELECT DISTINCT s.browser_id, s.visit_id, s.site_url FROM site_visits AS s;"
CRAWL = "SELECT DISTINCT c.task_id, c.browser_id FROM crawl AS c;"

CANVAS_JS = """SELECT sv.site_url, j.script_url, j.browser_id, j.symbol,
                        j.operation, j.value, j.arguments, j.time_stamp,
                        j.visit_id
                FROM javascript AS j
                INNER JOIN site_visits AS sv
                    ON sv.visit_id == j.visit_id
                WHERE j.symbol LIKE '%HTMLCanvasElement%'
                    OR j.symbol LIKE '%CanvasRenderingContext2D%'
                ORDER BY sv.site_url, j.script_url, j.time_stamp, j.browser_id;"""
JS_HTTP_URL = """SELECT DISTINCT j.script_url, h1.content_hash
                FROM javascript AS j
                INNER JOIN http_responses AS h1
                    ON h1.url == j.script_url
                WHERE j.symbol LIKE '%HTMLCanvasElement%'
                    OR j.symbol LIKE '%CanvasRenderingContext2D%'
                ORDER BY j.script_url"""
HTTP_SIZES = """SELECT DISTINCT h.url, h.headers
                FROM http_responses AS h
                INNER JOIN javascript AS j
                    ON j.script_url == h.url
                WHERE h.headers like '%content-length%'
                    AND (j.symbol LIKE '%HTMLCanvasElement%'
                        OR j.symbol LIKE '%CanvasRenderingContext2D%')"""

MATH_JS = """SELECT DISTINCT sv.site_url, j.script_url, j.browser_id, j.visit_id
            FROM javascript AS j
                INNER JOIN site_visits AS sv
                    ON sv.visit_id == j.visit_id
            WHERE j.symbol LIKE '%Math.random%'
            ORDER BY sv.site_url, j.script_url, j.browser_id;"""


def get_crawl_id() -> str:

    print("Selecting crawl_id...")

    marker = "INFO Starting Crawl ["
    crawl_id : str = None

    file_lines : list[str] = open_file(DCFP_LOG).readlines()

    for l in file_lines:
        if marker in l:
            tmp = l.split(marker)[1]
            crawl_id = tmp.split("]")[0]

            break
    
    print("\"" + crawl_id + "\"")
    print()

    return crawl_id

def level_db_to_json(crawl_id : str):

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

    dump_json(level_db, f"{crawl_id}_{EXT_LVLDB}", D_EXTRACT)

    print("LevelDB elements: {}".format(len(level_db)))
    print()


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

    if os.path.exists(src):
        print("Copying file...")
        print(f"SRC: {src}")
        print(f"DST: {dst}")
        print()

        if os.path.exists(dst):
            os.remove(dst)

        shutil.copyfile(src, dst)
        
    else:
        print(f"Copy SRC not found: {src}")
        print()

def get_query_data(query_data_name : str, query : str, first_only : bool = False):

    print(f"Extracting {query_data_name}...")

    result = get_from_db(query)

    if first_only:
        return [t[0] for t in result]
    else:
        return [t for t in result]

def sql_to_json(crawl_id):

    start = time.time()
    print("Get SQL Data")
    
    sql_data = {}
    sql_data["incomplete_visits"]   = get_query_data("incomplete_visits", INC_VISITS, True)
    sql_data["site_visits"]         = get_query_data("site_visits", SITE_VISITS)
    sql_data["crawl"]               = get_query_data("crawl", CRAWL)
    sql_data["canvas_js"]           = get_query_data("canvas_js", CANVAS_JS)
    sql_data["js_http_url"]         = get_query_data("js_http_url", JS_HTTP_URL)
    sql_data["http_sizes"]          = get_query_data("http_sizes", HTTP_SIZES)
    sql_data["math_js"]             = get_query_data("math_js", MATH_JS)

    end = time.time()
    print(f"SQL Extraction time: {end - start}s")
    start = end

    dump_json(sql_data, f"{crawl_id}_sql_data.json", D_EXTRACT)
    end = time.time()
    print(f"JSON Write time: {end - start}s")
    print()


def main():

    crawl_id = get_crawl_id()
    
    if crawl_id:
        copy_file(OWPM_LOG, D_EXTRACT / f"{crawl_id}_{OWP_LOG_NAME}")
        copy_file(DCFP_LOG, D_EXTRACT / f"{crawl_id}_{DCFP_LOG_NAME}")

        level_db_to_json(crawl_id)

        sql_to_json(crawl_id)

        #t.log("Some msg")
        #compress_sqlite()
        #Zip or compress sql...? and move it to extract? Move it and then compress all?

        #copy_file(OWPM_LOG, D_EXTRACT / OWP_NAME)
    else:
        print("No crawl_id found, extraction aborted")

if __name__ == "__main__":
    main()