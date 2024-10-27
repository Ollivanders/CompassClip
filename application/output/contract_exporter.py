from output.file_exporter import FileExporter


class ContractFileExporter(FileExporter):
    def export_item(self, item):
        item_type = item.get("type")
        if item_type is None:
            raise ValueError('"type" key is not found in item {}'.format(repr(item)))

        address = item.get("address")

        if address is None:
            raise RuntimeError("Contract address cannot be null")

        contract_address_key = f"contract/address/{address}"
        if contract_address_key not in self.file_mapping:
            self.open_file(contract_address_key)

        exporter = self.exporter_mapping.get(contract_address_key)
        if exporter is None:
            raise ValueError("Exporter for item type {} not found".format(item_type))
        exporter.export_item(item)

        counter = self.counter_mapping.get(contract_address_key)
        if counter is not None:
            counter.increment()
