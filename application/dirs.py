from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
BASE_DIR = THIS_DIR.parent
DATA_DIR = THIS_DIR / "data"


def chain_dir(chain):
    return DATA_DIR / chain


def transaction_file(chain):
    return DATA_DIR / chain / "transaction"


def contract_file(chain):
    return DATA_DIR / chain / "contract"


def block_file(chain):
    return DATA_DIR / chain / "block"


def transaction_partition_dir(chain, partition_key):
    par_dir = DATA_DIR / chain / "transaction_partitioned" / partition_key
    par_dir.mkdir(parents=True, exist_ok=True)
    return par_dir


def contract_partition_dir(chain, partition_key):
    par_dir = DATA_DIR / chain / "contract_partitioned" / partition_key
    par_dir.mkdir(parents=True, exist_ok=True)
    return par_dir


def block_partition_dir(chain, partition_key):
    par_dir = DATA_DIR / chain / "block_partitioned" / partition_key
    par_dir.mkdir(parents=True, exist_ok=True)
    return par_dir
