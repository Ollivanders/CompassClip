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
    reader = PartitionedReader("../sampledata/eth/partitioned/", "hash", 4)
    records = reader.get_records(
        "0x74ebd073bb3d30b7544f0b0a2201ffe4f45856943f2e9505b7094848a103067e"
    )
    print(records)
