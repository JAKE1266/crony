"""支持 ``python -m crony`` 直接运行。"""

import sys

from crony.cli import main

if __name__ == "__main__":
    sys.exit(main())
