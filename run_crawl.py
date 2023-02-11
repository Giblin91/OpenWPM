# CUSTOM CALO
import argparse
from custom.crawl_openwpm import main as crawl_openwpm

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="DCFP Crawler")
    # Const is used if -arg is passed without value (but needs nargs=? to work), Default is used if -arg not present
    parser.add_argument("-b", "--browsers",
                            nargs='?',
                            const=1,
                            default=1,
                            type=int,
                            help="N of browsers to spawn")

    parser.add_argument("-t", "--top",
                            nargs='?',
                            const=2,
                            default=2,
                            type=int,
                            help="Run crawl on top X selected url")

    parser.add_argument("-m", "--mobile",
                            action="store_true",
                            help="Run browsers as mobile emulation")

    parser.add_argument("-d", "--display_mode",
                            nargs='?',
                            const='xvfb',
                            default='xvfb',
                            choices=['native', 'headless', 'xvfb'],
                            help="Run in display mode as xvfb, headless, native")

    parser.add_argument("-c", "--cookies",
                            action="store_true",
                            help="Run crawl with accept cookies functionality")

    args = parser.parse_args()
    #print(args)
    # LOR
    
    crawl_openwpm(args)

if __name__ == "__main__":
    main()
