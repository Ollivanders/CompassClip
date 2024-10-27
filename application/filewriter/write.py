import json
from pathlib import Path


def matches(o, key, value):
    if key in o and o[key] == value:
        return True
    return False


def append_json(new_data, filename="data.json"):
    print(f"appending to {filename}")
    with open(filename, "r+") as file:
        # First we load existing data into a dict.
        file_data = json.load(file)

        print(file_data)

        if len([x for x in file_data if matches(x, "hash", new_data["hash"])]) > 0:
            print(f"Not appending to {filename} as {new_data['hash']} already in file")
            return

        # Join new_data with file_data inside emp_details
        file_data.append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file)


def write_split(filename, destination_folder, depth=4, filemode="a"):
    depth = depth + 2  # ignore the 0x starting chars

    with open(filename, "r") as f:
        records = f.readlines()

    for line in records:
        record = json.loads(line)
        hash = record["hash"]

        dest_path = Path(destination_folder)
        dest_filename = dest_path / Path(hash[:depth] + ".json")

        if dest_filename.is_file():
            append_json(record, str(dest_filename))

        else:
            with open(dest_filename, filemode) as df:
                json.dump([record], df)


if __name__ == "__main__":
    write_split(
        "../sampledata/eth/transactions.json", "../sampledata/eth/partitioned/", 2, "a"
    )
