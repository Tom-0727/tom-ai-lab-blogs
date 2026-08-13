#!/usr/bin/env python3
"""Upload a public blog image to Tencent Cloud COS."""

from __future__ import annotations

import argparse
import mimetypes
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])$")


def load_env_file(path: Path) -> None:
    """Load missing variables from a simple dotenv file without exposing values."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def slug(value: str, label: str) -> str:
    if not SLUG_PATTERN.fullmatch(value):
        raise ValueError(f"{label} must use lowercase letters, digits, and single hyphens")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload an image to blog/YYYY/MM/<article-slug>/ in Tencent COS."
    )
    parser.add_argument("file", type=Path, help="Local image path")
    parser.add_argument("--article-slug", required=True, help="Lowercase post slug")
    parser.add_argument("--date", required=True, help="Publication month in YYYY-MM format")
    parser.add_argument("--name", help="Destination basename without extension")
    parser.add_argument("--alt", default="", help="Alt text for emitted Markdown")
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip-url-check", action="store_true")
    return parser.parse_args()


def verify_public_url(url: str) -> None:
    request = Request(url, method="HEAD", headers={"User-Agent": "blog-cos-uploader/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            if not 200 <= response.status < 400:
                raise RuntimeError(f"Public URL returned HTTP {response.status}")
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Could not access public URL: {exc}") from exc


def main() -> int:
    args = parse_args()
    load_env_file(args.env_file)

    source = args.file.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"File does not exist: {source}")

    article_slug = slug(args.article_slug, "--article-slug")
    name = slug(args.name or source.stem.lower().replace("_", "-"), "--name")
    match = DATE_PATTERN.fullmatch(args.date)
    if not match:
        raise ValueError("--date must use YYYY-MM format")

    content_type, _ = mimetypes.guess_type(source.name)
    if not content_type or not content_type.startswith("image/"):
        raise ValueError(f"Unsupported or unknown image type: {source.suffix or '(none)'}")

    bucket = required_env("COS_BUCKET")
    region = required_env("COS_REGION")
    base_url = required_env("COS_BASE_URL").rstrip("/")
    secret_id = required_env("COS_SECRET_ID")
    secret_key = required_env("COS_SECRET_KEY")

    try:
        from qcloud_cos import CosConfig, CosS3Client
        from qcloud_cos.cos_exception import CosServiceError
    except ImportError as exc:
        raise RuntimeError(
            "Tencent COS SDK is missing. Run this script with: "
            "uv run --with cos-python-sdk-v5 python3 <script> ..."
        ) from exc

    extension = source.suffix.lower()
    key = (
        f"blog/{match.group('year')}/{match.group('month')}/"
        f"{article_slug}/{name}{extension}"
    )
    client = CosS3Client(
        CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Scheme="https",
        )
    )

    if not args.overwrite:
        try:
            client.head_object(Bucket=bucket, Key=key)
        except CosServiceError as exc:
            if exc.get_status_code() != 404:
                raise
        else:
            raise FileExistsError(
                f"COS object already exists: {key}. Pass --overwrite to replace it."
            )

    with source.open("rb") as body:
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
            ContentDisposition="inline",
        )

    encoded_key = quote(key, safe="/")
    url = f"{base_url}/{encoded_key}"
    if not args.skip_url_check:
        verify_public_url(url)

    print(f"Object key: {key}")
    print(f"Public URL: {url}")
    print(f"Markdown: ![{args.alt}]({url})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
