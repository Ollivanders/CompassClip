import shutil
from dirs import DATA_DIR
from constants import ANKR_KEY


# eth
# polygon
def get_provider_uri(chain):
    return f"https://rpc.ankr.com/{chain}/{ANKR_KEY}"


def refresh_data_dir():
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
