import json
from pathlib import Path


class PartitionedWriter:
    def __init__(self, destination_folder, partition_key, partition_depth=4) -> None:
        self.destination_folder = destination_folder
        self.partition_key = partition_key
        self.partition_depth = partition_depth

    @staticmethod
    def matches(o, key, value):
        if key in o and o[key] == value:
            return True
        return False

    @staticmethod
    def append_json(new_data, path: Path):
        with path.open("r+") as file:
            # First we load existing data into a dict.
            file_data = json.load(file)

            if (
                len(
                    [
                        x
                        for x in file_data
                        if PartitionedWriter.matches(x, "hash", new_data["hash"])
                    ]
                )
                > 0
            ):
                return

            # Join new_data with file_data inside emp_details
            file_data.append(new_data)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file)



    def write_split(self, record_source):
        """Partition a json file into multiple files based on the partition key

        args:
        filename - source json file to load from
        """
        for record in record_source:
        
            hash = record["hash"]

            dest_path = Path(self.destination_folder)
            dst_path = dest_path / Path(hash[: self.partition_depth] + ".json")

            if dst_path.is_file():
                PartitionedWriter.append_json(record, dst_path)

            else:
                # otherwise create the file
                with dst_path.open("w") as df:
                    json.dump([record], df)

    # def rewrite_partitions(self, depth=4):


if __name__ == "__main__":

    def read_source(filename):
        path = Path(filename)
        with path.open("r") as f:
            for line in f:
                yield json.loads(line)

    writer = PartitionedWriter("../sampledata/eth/partitioned/", "hash")
    writer.write_split(
        read_source("../sampledata/eth/transactions.json")
    )
