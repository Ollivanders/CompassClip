import json
from pathlib import Path

import logging

class PartitionedReader:
    def __init__(self, archive_location, partition_key_function, matching_function) -> None:
        self.archive_location = archive_location
        self.partition_key_function = partition_key_function
        self.matching_function = matching_function
        self._read_depth_file()

    def _get_depth_path(self):
        return Path(self.archive_location) / Path("partition_depth.txt")

    def _read_depth_file(self):
        path = self._get_depth_path()
        if path.is_file():
            with path.open("r") as f:
                self.partition_depth = int(f.read())

    def get_records(self, search_record):
        path = Path(self.archive_location) / Path(
            self.partition_key_function(search_record)[: self.partition_depth] + ".json"
        )

        if not path.is_file():
            return []

        with path.open("r") as f:
            records = json.load(f)
            print([r["block_number"] for r in records])
            return [r for r in records if self.matching_function(search_record, r)]


if __name__ == "__main__":
    pass
    # reader = PartitionedReader(transaction_partition_dir("eth", "hash"), "hash")
    # records = reader.get_records(
    #     "0x74ebd073bb3d30b7544f0b0a2201ffe4f45856943f2e9505b7094848a103067e"
    # )
    # print(records)
