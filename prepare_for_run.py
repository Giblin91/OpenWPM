from custom.File_Helper import (check_create_dir, check_remove_dir, check_remove_file,
                                ROOT, DATADIR, D_EXTRACT, LEVELDB, OWPM_LOG, SQLITE, DCFP_LOG, EXT_LVLDB)

print("Preparing for crawl...")

if check_create_dir(DATADIR):
    print(f"{DATADIR} already exists")

    check_remove_dir(LEVELDB)
    check_remove_file(OWPM_LOG)
    check_remove_file(SQLITE)
    check_remove_file(DATADIR / "crawl-data.sqlite-journal")
else:
    print(f"{DATADIR} created")

if check_create_dir(D_EXTRACT):
    print(f"{D_EXTRACT} already exists") 

    check_remove_file(DCFP_LOG)
    check_remove_file(EXT_LVLDB)
else:
    print(f"{D_EXTRACT} created")

check_remove_file(ROOT / "geckodriver.log")