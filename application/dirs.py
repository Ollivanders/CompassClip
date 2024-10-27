from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
BASE_DIR = THIS_DIR.parent
DATA_DIR = THIS_DIR / "data"


def transaction_file(chain):
    return DATA_DIR / chain / "transaction"


def transaction_partition_dir(chain, partition_key):
    par_dir = DATA_DIR / chain / "transaction_partitioned" / partition_key
    par_dir.mkdir(parents=True, exist_ok=True)
    return par_dir
