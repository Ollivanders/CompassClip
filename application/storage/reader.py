import json
from pathlib import Path


class PartitionedReader:
    def __init__(self, archive_location, partition_key, partition_depth) -> None:
        self.archive_location = archive_location
        self.partition_key = partition_key
        self.partition_depth = partition_depth

    def get_records(self, search_value):
        path = Path(self.archive_location) / Path(
            search_value[: self.partition_depth] + ".json"
        )

        if not path.is_file():
            return []

        with path.open("r") as f:
            records = json.load(f)
            return [r for r in records if r[self.partition_key] == search_value]


if __name__ == "__main__":
    reader = PartitionedReader("../sampledata/eth/partitioned/", "hash", 6)
    records = reader.get_records(
        "0x2b0da7b682a2a76e143f9d922c87566be499c53055dd832eef5ab4302d4deaa1"
    )
    print(records)
