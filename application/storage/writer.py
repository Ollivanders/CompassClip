import json
from pathlib import Path


class PartitionedWriter:
    def __init__(self, destination_folder, partition_key, partition_depth=4, dynamic_depth=True, dynamic_depth_limit=20) -> None:
        self.destination_folder = destination_folder
        self.partition_key = partition_key
        self.partition_depth = partition_depth
        self.dynamic_depth = dynamic_depth
        self.dynamic_depth_limit = dynamic_depth_limit

        self._initialize_target_dir()

        if dynamic_depth:
            self._read_depth_file()
        self._write_depth_file()


    def _initialize_target_dir(self):
        Path(self.destination_folder).mkdir(parents=True, exist_ok=True)

    def _get_depth_path(self):
        return Path(self.destination_folder) / Path("partition_depth.txt")

    def _read_depth_file(self):
        path = self._get_depth_path()
        if path.is_file():
            with path.open('r') as f:
                self.partition_depth = int(f.read())

    def _write_depth_file(self):
        path = self._get_depth_path() 
        with path.open('w') as f:
            f.write(str(self.partition_depth))

    @staticmethod
    def matches(o, key, value):
        if key in o and o[key] == value:
            return True
        return False

    def append_json(self, new_data, path: Path):
        with path.open("r+") as file:
            # First we load existing data into a dict.
            file_data = json.load(file)

            if (
                len(
                    [
                        x
                        for x in file_data
                        if PartitionedWriter.matches(x, self.partition_key, new_data[self.partition_key])
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

            if self.dynamic_depth and len(file_data) > self.dynamic_depth_limit:
                new_depth = self.partition_depth + 1
                PartitionedWriter.rewrite_partitions(self, PartitionedWriter(self.destination_folder, self.partition_key, new_depth, False, self.dynamic_depth_limit))
                self.partition_depth = new_depth


    def write_split(self, record_source):
        """Partition a json source into multiple files based on the partition key

        args:
        record_source - an iterator yielding json records
        """
        for record in record_source:
            key = record[self.partition_key]

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
        
        def iterator(path):
            with path.open('r') as f:
                for record in json.load(f):
                    yield record

        for c in current_files:
            new_writer.write_split(iterator(c))
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

    writer = PartitionedWriter("../sampledata/eth/partitioned-contracts/", "address", partition_depth=4, dynamic_depth=True, dynamic_depth_limit=20)
    writer.write_split(
        read_source("../sampledata/eth/contracts.json")
    )
