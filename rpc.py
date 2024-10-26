from ethereumetl.json_rpc_requests import generate_json_rpc


def generate_get_storage_attr_json_rpc(contract_addresses, block="latest"):
    for idx, contract_address in enumerate(contract_addresses):
        yield generate_json_rpc(
            method="eth_getStorageAttr",
            params=[contract_address, hex(block) if isinstance(block, int) else block],
            request_id=idx,
        )
