import hashlib

def contract_partition_key(record):
        try:
            a = record["address"]
            b = record["block_number"]
            m = hashlib.sha256()
            m.update((a + str(b)).encode())
            return m.hexdigest()
        except Exception as e:
            print(record)
            raise e


def contract_equality(record_a, record_b):
    return record_a["address"] == record_b["address"] and record_a["block_number"] == record_b["block_number"]