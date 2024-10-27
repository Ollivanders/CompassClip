from constants import ANKR_KEY


# eth
# polygon
def get_provider_uri(chain):
    return f"https://rpc.ankr.com/{chain}/{ANKR_KEY}"
