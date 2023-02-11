# CUSTOM CALO
import argparse
from custom.crawl_openwpm import main as crawl_openwpm

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="dcfp_crawler")
    # Const is used if -b is passed without int, Default is used if -b not present
    parser.add_argument("-b", "--browsers", nargs='?', const=1, default=1, type=int, help="N of browsers to spawn")
    parser.add_argument("-t", "--top", type=int, help="Run crawl on top X selected url")
    parser.add_argument("-m", "--mobile", action="store_true", help="Run browsers as mobile emulation")
    parser.add_argument("-x", "--xvfb", action="store_true", help="Run as xvfb - virtual screen")
    parser.add_argument("-c", "--cookies", action="store_true", help="Run crawl with accept cookies functionality")
    # browser param/instrument? js, http capture?

    args = parser.parse_args()
    print(args)
    
    crawl_openwpm(args)

if __name__ == "__main__":
    main()
