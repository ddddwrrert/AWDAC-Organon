import sys
from awdac.cli import main

if __name__ == "__main__":
    main(['ablate', *sys.argv[1:]])
