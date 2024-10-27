from pathlib import Path
import json


def read_partitioned(archive_location, hash, depth=4):
    depth = depth + 2

    path = Path(archive_location) / Path(hash[:depth] + ".json")

    pass
