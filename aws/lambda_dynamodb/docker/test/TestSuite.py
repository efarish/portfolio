import sys

import pytest
from dotenv import load_dotenv

sys.path.append('docker/util')

load_dotenv()

if __name__ == "__main__":
    pytest.main()