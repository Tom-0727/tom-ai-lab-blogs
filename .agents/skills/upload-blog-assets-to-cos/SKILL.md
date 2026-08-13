---
name: upload-blog-assets-to-cos
description: Upload image assets for this Hexo blog to Tencent Cloud COS and return a public URL or ready-to-paste Markdown. Use when adding local screenshots, illustrations, covers, or other image files to a blog post, replacing an image placeholder, or publishing blog media through COS.
---

# Upload Blog Assets to COS

Use `scripts/upload_cos.py` for deterministic uploads. Keep COS credentials and deployment-specific settings in the repository-root `.env`; never place their values in a post, commit, command output, or skill file.

## Upload workflow

1. Identify the target post slug and its publication month from the post front matter.
2. Choose a short lowercase English filename using hyphens. Preserve the source extension unless conversion was explicitly requested.
3. Run the script from the repository root:

```bash
uv run --with cos-python-sdk-v5 \
  python3 .agents/skills/upload-blog-assets-to-cos/scripts/upload_cos.py \
  /absolute/path/to/image.png \
  --article-slug cloudcli-ai-native-development-anywhere \
  --date 2026-08 \
  --name cloudcli-workspaces \
  --alt "CloudCLI 中的项目工作区和 Session 管理"
```

4. Use the emitted Markdown in the post only after the script reports that public URL verification succeeded.
5. Do not upload again when the intended object already exists. The script refuses overwrite by default; use `--overwrite` only when the user explicitly intends to replace that exact object.

Objects use this layout:

```text
blog/YYYY/MM/<article-slug>/<filename.ext>
```

## Configuration

Require these values in the repository-root `.env`:

```dotenv
COS_SECRET_ID=...
COS_SECRET_KEY=...
COS_BUCKET=...
COS_REGION=...
COS_BASE_URL=https://...
```

`COS_BASE_URL` may be the COS default domain or a later custom/CDN domain. The script combines it with the object key, so do not include a path after the host.

Use `uv` to load the official SDK without modifying the system Python environment:

```bash
uv run --with cos-python-sdk-v5 python3 scripts/upload_cos.py --help
```

## Safety

- Treat every uploaded image as public.
- Inspect images for unintended secrets or personal information before uploading.
- Never print credential values.
- Keep `.env` ignored by Git.
- Prefer a restricted CAM sub-account that can only upload/read objects under the blog asset prefix.
- Preserve unrelated working-tree changes when updating a post.
