import subprocess

from dirs import DATA_DIR
from utils import refresh_data_dir

BUCKET_NAME = "compassclips"


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
    # wipe data dir first
    refresh_data_dir()
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


# print("Starting sync from local to S3...")
# sync_local_to_s3()

print("Starting sync from S3 to local...")
sync_s3_to_local()
