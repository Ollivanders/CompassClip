import itertools
import logging

from dirs import DATA_DIR
from output.json_export import JsonExport

DATA_TYPES = (
    "block",
    "transaction",
    "contract",
)


class AtomicCounter:
    def __init__(self):
        self._counter = itertools.count()
        next(self._counter)

    def increment(self, increment=1):
        assert increment > 0
        return [next(self._counter) for _ in range(0, increment)][-1]


class FileExporter:
    def __init__(self, chain, data_types=[]):
        for data_type in data_types:
            assert data_type in DATA_TYPES
        self.data_types = data_types

        self.chain = chain
        self.exporter_mapping = {}
        self.counter_mapping = {}

        self.file_mapping = {}

        self.logger = logging.getLogger("FileExporter")
        self.open()

    def get_data_path(self, item_key: str):
        data_path = DATA_DIR / self.chain / item_key
        data_path.parent.mkdir(parents=True, exist_ok=True)
        return data_path

    def open(self):
        for item_type in self.data_types:
            self.open_file(item_type)

    def open_file(self, item_key):
        filepath = self.get_data_path(item_key)
        file = open(filepath, "wb")

        self.file_mapping[item_key] = file
        self.exporter_mapping[item_key] = JsonExport(file)
        self.counter_mapping[item_key] = AtomicCounter()

    def export_item(self, item):
        item_type = item.get("type")

        if item_type is None:
            raise ValueError('"type" key is not found in item {}'.format(repr(item)))

        exporter = self.exporter_mapping.get(item_type)
        if exporter is None:
            raise ValueError("Exporter for item type {} not found".format(item_type))
        exporter.export_item(item)

        counter = self.counter_mapping.get(item_type)
        if counter is not None:
            counter.increment()

    def close(self):
        for item_type, file in self.file_mapping.items():
            file.close()

            counter = self.counter_mapping[item_type]
            if counter is not None:
                self.logger.info(
                    "{} items exported: {}".format(item_type, counter.increment() - 1)
                )
