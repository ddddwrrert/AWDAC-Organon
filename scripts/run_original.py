import sys
from awdac.cli import main

if __name__ == "__main__":
    main(['inspect-original', *sys.argv[1:]])
