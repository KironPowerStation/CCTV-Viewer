import os
import base64

import boto3
from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)


def get_s3_client():
    """Create an S3 client using environment configuration.

    If no credentials are provided (public bucket), the client uses unsigned requests.
    """
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION")
    endpoint = os.getenv("S3_ENDPOINT_URL")

    if not access_key and not secret_key:
        return boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint,
            config=Config(signature_version=UNSIGNED),
        )

    session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )
    return session.client("s3", endpoint_url=endpoint)


def get_encoded_demo_secret():
    """Return a base64-encoded demo secret payload."""
    secret_key = os.getenv("DEMO_SECRET_KEY", "demo-key")
    secret_value = os.getenv("DEMO_SECRET_VALUE", "demo-value")
    payload = f"{secret_key}:{secret_value}".encode("utf-8")
    return base64.b64encode(payload).decode("ascii")


def get_bucket_and_prefix():
    bucket = os.getenv("S3_BUCKET")
    prefix = os.getenv("S3_PREFIX", "").strip()
    if prefix and not prefix.endswith("/"):
        prefix = prefix + "/"
    return bucket, prefix


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/videos")
def list_videos():
    bucket, prefix = get_bucket_and_prefix()
    if not bucket:
        return jsonify({"error": "S3_BUCKET is not configured"}), 500

    client = get_s3_client()
    try:
        paginator = ("list_objects_v2")
        page_iter = (Bucket=bucket, Prefix=prefix)
        videos = []
        for page in page_iter:
            contents = page.get("Contents") or []
            for obj in contents:
                key = obj.get("Key", "")
                if not key.lower().endswith(".mp4"):
                    continue
                display_name = (
                    key[len(prefix) :] if prefix and key.startswith(prefix) else key
                )
                videos.append(
                    {"key": key, "name": display_name, "size": obj.get("Size", 0)}
                )
    except (BotoCoreError, ClientError) as exc:
        return jsonify({"error": f"S3 list error: {exc}"}), 502

    return jsonify({"videos": videos})


@app.route("/api/videos/url")
def get_video_url():
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "key is required"}), 400
    if not bucket:
        return jsonify({"error": "S3_BUCKET is not configured"}), 500

    expires = int(os.getenv("S3_URL_EXPIRY_SECONDS", "3600"))
    client = get_s3_client()
    try:
        presigned_url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires,
        )
    except (BotoCoreError, ClientError) as exc:
        return jsonify({"error": f"S3 presign error: {exc}"}), 502

    return jsonify({"url": presigned_url})

@app.route("/api/write/data")
def write_data():
    encode = get_encoded_value()
    return jsonify({"name": "write_data", "encoded": encoded_value})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG") == "1")
