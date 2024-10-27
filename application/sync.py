import subprocess
from datetime import datetime, timezone

import boto3
from utils import refresh_data_dir
from dirs import DATA_DIR

BUCKET_NAME = "compassclip"


def sync_local_to_s3():
    """Sync local directory to S3."""
    try:
        result = subprocess.run(
            ["aws", "s3", "sync", DATA_DIR, f"s3://{BUCKET_NAME}"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Sync local to S3 completed successfully:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error during sync local to S3:")
        print(e.stderr)


def sync_s3_to_local():
    """Sync S3 bucket to local directory."""
    try:
        result = subprocess.run(
            ["aws", "s3", "sync", f"s3://{BUCKET_NAME}", DATA_DIR, "--no-sign-request"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Sync S3 to local completed successfully:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error during sync S3 to local:")
        print(e.stderr)


s3 = boto3.client("s3")


def download_from_s3():
    """Download files from S3 bucket to local directory using pathlib, similar to `aws s3 sync`."""
    paginator = s3.get_paginator("list_objects_v2")

    # Make sure the base directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for page in paginator.paginate(Bucket=BUCKET_NAME):
        for obj in page.get("Contents", []):
            s3_path = obj["Key"]
            local_path = DATA_DIR / s3_path

            # Ensure local directory structure exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if the file exists locally and if it's up-to-date
            if not local_path.exists():
                print(f"Downloading {s3_path} to {local_path}...")
                s3.download_file(BUCKET_NAME, s3_path, str(local_path))
            else:
                # Compare timestamps to see if the S3 file is newer
                s3_mtime = obj["LastModified"]
                local_mtime = datetime.fromtimestamp(
                    local_path.stat().st_mtime, timezone.utc
                )

                if s3_mtime > local_mtime:
                    print(f"Updating {s3_path} to {local_path}...")
                    s3.download_file(BUCKET_NAME, s3_path, str(local_path))
                else:
                    print(f"{s3_path} is already up-to-date.")


refresh_data_dir()

print("Starting download from S3 bucket to local directory...")
download_from_s3()
print("Download complete.")

# print("Starting sync from local to S3...")
# sync_local_to_s3(DATA_DIR, BUCKET_NAME)

# print("Starting sync from S3 to local...")
# sync_s3_to_local()
