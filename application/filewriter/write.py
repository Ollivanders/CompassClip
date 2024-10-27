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
    def append_json(new_data, filename="data.json"):
        with open(filename, "r+") as file:
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

    def write_split(self, filename):
        """Partition a json file into multiple files based on the partition key

        args:
        filename - source json file to load from
        destination_folder - destination directory to write partitioned data to
        partition_key - the name of the partition key in the json objects
        depth - the number of characters to from the partition key
        """
        with open(filename, "r") as f:
            records = f.readlines()

        for line in records:
            record = json.loads(line)
            hash = record["hash"]

            dest_path = Path(self.destination_folder)
            dest_filename = dest_path / Path(hash[: self.partition_depth] + ".json")

            if dest_filename.is_file():
                PartitionedWriter.append_json(record, str(dest_filename))

            else:
                # otherwise create the file
                with open(dest_filename, "w") as df:
                    json.dump([record], df)


if __name__ == "__main__":
    write_split(
        "../sampledata/eth/transactions.json", "../sampledata/eth/partitioned/", "hash"
    )
