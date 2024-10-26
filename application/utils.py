from constants import ANKR_KEY
from dirs import DATA_DIR


# eth
# polygon
def get_provider_uri(chain):
    return f"https://rpc.ankr.com/{chain}/{ANKR_KEY}"


def get_data_path(chain, type: str):
    data_path = DATA_DIR / chain / f"{type}.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    return data_path
