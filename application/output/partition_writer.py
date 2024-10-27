import json
from pathlib import Path
import logging
import hashlib

class PartitionedWriter:
    def __init__(self, destination_folder, partition_function, matching_function, partition_depth=1, dynamic_depth=True, dynamic_depth_limit=128) -> None:
        self.destination_folder = destination_folder
        self.partition_function = partition_function
        self.matching_function = matching_function
        self.partition_depth = partition_depth
        self.dynamic_depth = dynamic_depth
        self.dynamic_depth_limit = dynamic_depth_limit

        self._initialize_target_dir()

        if dynamic_depth:
            self._read_depth_file()
        self._write_depth_file()

    def _initialize_target_dir(self):
        logging.debug(f"Initializing destination direction {self.destination_folder}")
        Path(self.destination_folder).mkdir(parents=True, exist_ok=True)

    def _get_depth_path(self):
        return Path(self.destination_folder) / Path("partition_depth.txt")

    def _read_depth_file(self):
        path = self._get_depth_path()
        if path.is_file():
            with path.open('r') as f:
                partition_depth = int(f.read())
                logging.debug(f"Found parition depth for {self.destination_folder} as {partition_depth} from {path}")
                self.partition_depth = partition_depth
        else:
            logging.debug(f"Did not find a partition depth entry in {self.destination_folder}")

    def _write_depth_file(self):
        path = self._get_depth_path() 
        with path.open('w') as f:
            logging.debug(f"Writing parition depth for {self.destination_folder} as {self.partition_depth} to {path}")
            f.write(str(self.partition_depth))

    def append_json(self, new_data, path: Path):
        with path.open("r+") as file:
            # First we load existing data into a dict.
            file_data = json.load(file)

            if len([x for x in file_data if self.matching_function(new_data, x)]) > 0:
                return

            # Join new_data with file_data inside emp_details
            file_data.append(new_data)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file)

            if self.dynamic_depth and len(file_data) > self.dynamic_depth_limit:
                new_depth = self.partition_depth + 1
                PartitionedWriter.rewrite_partitions(
                    self,
                    PartitionedWriter(
                        self.destination_folder,
                        self.partition_function,
                        self.matching_function,
                        new_depth,
                        False,
                        self.dynamic_depth_limit,
                    ),
                )
                self.partition_depth = new_depth

    def write_split(self, record_source):
        """Partition a json source into multiple files based on the partition key

        args:
        record_source - an iterator yielding json records
        """
        for record in record_source:
            key = self.partition_function(record)

            dest_path = Path(self.destination_folder)
            dst_path: Path = dest_path / Path(key[: self.partition_depth] + ".json")

            if dst_path.is_file():
                self.append_json(record, dst_path)

            else:
                # otherwise create the file
                with dst_path.open("w") as df:
                    json.dump([record], df)

    @staticmethod
    def rewrite_partitions(old_writer, new_writer):
        current_files = Path(old_writer.destination_folder).glob('*.json')

        current_files = [c for c in current_files if len(c.stem) == old_writer.partition_depth]
        
        def iterator(path):
            with path.open("r") as f:
                try:
                    for record in json.load(f):
                        yield record
                except Exception as e:
                    with path.open('r') as g:
                        print(g.readlines())
                        print(path)
                        raise e

        for c in current_files:
            new_writer.write_split(iterator(c))

        for c in current_files:
            c.unlink()


def read_source(filename):
    path = Path(filename)
    with path.open("r") as f:
        for line in f:
            yield json.loads(line)


if __name__ == "__main__":
    def read_source(filename):
        path = Path(filename)
        with path.open("r") as f:
            for line in f:
                yield json.loads(line)

    # writer = PartitionedWriter("../sampledata/eth/partitioned-contracts/", key_fn, equality_fn,  partition_depth=4, dynamic_depth=True, dynamic_depth_limit=128)
    # writer.write_split(
    #     read_source("../sampledata/eth/contracts.json")
    # )
    # writer.write_split(read_source("../sampledata/eth/contracts.json"))
