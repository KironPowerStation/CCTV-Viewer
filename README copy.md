# Kiron Nuclear Video Viewer

A minimal Flask app that lists `.mp4` files from an S3 bucket and plays them through presigned URLs. Built for CT25 demo flavor—includes a harmless, clearly fake credential for scavenger hunts.

## Quick start
1. Copy `.env.example` to `.env` and fill in your S3 details.
2. Build and run: `docker-compose up --build`.
3. Open `http://localhost:5000` and pick a clip from the list.

### Environment
- `S3_BUCKET` (required)
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` (optional; omit for public buckets)
- `S3_PREFIX` (optional, e.g., `videos/`)
- `S3_ENDPOINT_URL` (optional for custom endpoints)
- `S3_URL_EXPIRY_SECONDS` (presigned URL lifetime; default 3600)

> Note: Do not place real secrets in the repo. The baked-in `KIRON_FAKE_ROOT` value is intentionally bogus for CTF flavor only.
