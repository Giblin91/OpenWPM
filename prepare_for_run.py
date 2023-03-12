from custom.File_Helper import (check_create_dir, check_remove_dir, check_remove_file,
                                ROOT, DATADIR, D_EXTRACT, LEVELDB, OWPM_LOG, SQLITE, DCFP_LOG)

print("Preparing for crawl...")

if check_create_dir(DATADIR):
    print(f"{DATADIR} already exists")

    check_remove_dir(LEVELDB)
    check_remove_file(OWPM_LOG)
    check_remove_file(SQLITE)
    # Note sqllite journal will not be removed
else:
    print(f"{DATADIR} created")

if check_create_dir(D_EXTRACT):
    print(f"{D_EXTRACT} already exists") 

    check_remove_file(DCFP_LOG)
else:
    print(f"{D_EXTRACT} created")

check_remove_file(ROOT / "geckodriver.log")
check_remove_file(ROOT / "mohup.out")