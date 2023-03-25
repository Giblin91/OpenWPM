from custom.File_Helper import (check_create_dir, check_remove_dir, check_remove_file,
                                ROOT, DATADIR, D_EXTRACT, D_CANVAS, LEVELDB, OWPM_LOG, SQLITE, DCFP_LOG, EXT_LVLDB)


resp = input("This step will clean all existing crawl data. Do you really wish to continue? [y/n]\n")

if resp.casefold() == "y":

    print("Preparing envirnment for a new crawl...")

    # datadir
    if check_create_dir(DATADIR):
        print(f"{DATADIR} already exists")

        check_remove_dir(LEVELDB)
        check_remove_dir(D_EXTRACT)
        check_remove_file(OWPM_LOG)
        check_remove_file(SQLITE)
        check_remove_file(DATADIR / "crawl-data.sqlite-journal")
    else:
        print(f"{DATADIR} created")

    # datadir/extract
    check_create_dir(D_EXTRACT)


    check_remove_file(ROOT / "geckodriver.log")

else:
    print("Preparation process aborted")