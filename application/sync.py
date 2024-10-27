import subprocess

from dirs import DATA_DIR

BUCKET_NAME = "compassclip"


def sync_local_to_s3(local_dir, bucket_name):
    """Sync local directory to S3."""
    try:
        result = subprocess.run(
            ["aws", "s3", "sync", local_dir, f"s3://{bucket_name}"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Sync local to S3 completed successfully:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error during sync local to S3:")
        print(e.stderr)


def sync_s3_to_local(bucket_name, local_dir):
    """Sync S3 bucket to local directory."""
    try:
        result = subprocess.run(
            ["aws", "s3", "sync", f"s3://{bucket_name}", local_dir],
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
# sync_local_to_s3(DATA_DIR, BUCKET_NAME)

print("Starting sync from S3 to local...")
sync_s3_to_local(BUCKET_NAME, DATA_DIR)
