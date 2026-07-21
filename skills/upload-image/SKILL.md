---
name: upload-image
description: Upload a local image (screenshot, diagram, gif) and get back a public URL to embed in a GitHub PR description, issue, or any markdown. Commits the image into a GitHub repo via the contents API and returns its raw.githubusercontent.com URL. Use when the user asks to upload/host an image, get a URL for a screenshot, or embed a local image in a PR/issue.
---

# Upload Image

Host a local image publicly and return a URL you can paste into a GitHub PR
description, issue, or markdown doc.

The image is committed into a **public GitHub repo that acts as an image bucket**
and served from `raw.githubusercontent.com`. At Cline that bucket is
**`cline/assets-internal`**; if you use this skill elsewhere, point it at any
public repo you can push to.

> **Requirement:** you need **write (push) access to the bucket repo**. The skill
> commits the file, so `gh` must be authenticated as an account that can push to
> it. For `cline/assets-internal` that means being a Cline org member. Without
> write access the upload fails with `403`.

## Why commit via the contents API (and not imgur / gh release upload)

- **imgur** no longer allows free API uploads.
- **`gh release upload`** works on a normal machine but goes to
  `uploads.github.com`, which some restricted/sandboxed environments (including
  agent sandboxes behind an auth proxy) don't authenticate — you get
  `401 Bad credentials`. The **contents API** goes through `api.github.com`,
  which works everywhere. So committing the file is the portable path.
- The bucket must be **public** so the raw URLs render for anyone reading the PR
  (a private repo's URLs require auth and show as broken images).

## Prerequisites

```bash
gh auth status   # must be authed with push access to the bucket repo
```

## Upload

Set `REPO` to your bucket repo, then commit the image under `images/` with a
collision-proof name and build the raw URL.

```bash
REPO="cline/assets-internal"              # your public bucket repo
SRC="/absolute/path/to/screenshot.png"    # the local file to upload

# sanitize the name (drop spaces/colons) and timestamp-prefix it for uniqueness
CLEAN=$(basename "$SRC" | tr ' :' '--')
DEST="images/$(date +%Y%m%d-%H%M%S)-${CLEAN}"

# base64 the binary into a JSON payload file (avoids argv length limits on large images)
python3 -c "import json,base64,sys; print(json.dumps({'message':'add '+sys.argv[2], 'content':base64.b64encode(open(sys.argv[1],'rb').read()).decode()}))" \
  "$SRC" "$DEST" > /tmp/upload-image-payload.json

# commit via the contents API
gh api "repos/$REPO/contents/$DEST" -X PUT \
  --input /tmp/upload-image-payload.json --jq '.commit.sha' >/dev/null
rm -f /tmp/upload-image-payload.json

BRANCH=$(gh api "repos/$REPO" --jq '.default_branch')
URL="https://raw.githubusercontent.com/$REPO/${BRANCH}/${DEST}"
echo "$URL"
```

### Verify (recommended)

```bash
curl -sL -o /dev/null -w "HTTP %{http_code}, %{size_download} bytes\n" "$URL"
# expect: HTTP 200 with a nonzero byte count
```

## Return the result to the user

Give them the bare URL plus a ready-to-paste markdown snippet:

```
https://raw.githubusercontent.com/cline/assets-internal/main/images/20260721-024207-screenshot.png

Markdown for a PR/issue:
![screenshot](https://raw.githubusercontent.com/cline/assets-internal/main/images/20260721-024207-screenshot.png)
```

If they named a specific PR/issue, offer to insert it directly (edit the body,
then `gh pr edit <number> --body-file /tmp/body.md`).

## Multiple images

Loop over each file, upload, and collect all URLs. One commit per file is fine —
the bucket repo doesn't care about commit count.

## Notes & limits

- **Formats:** anything GitHub renders — PNG, JPG, GIF (animated works), WEBP, SVG.
- **Size:** the contents API accepts files up to 100 MB, but base64 inflates the
  payload ~33% and anything over a few MB is slow. For big screenshots, offer to
  downscale first: `sips -Z 2000 img.png` (macOS) or
  `convert img.png -resize 2000x2000\> out.png` (ImageMagick).
- **Deleting an image later:**
  ```bash
  SHA=$(gh api "repos/$REPO/contents/<path>" --jq '.sha')
  gh api "repos/$REPO/contents/<path>" -X DELETE -f message="remove image" -f sha="$SHA"
  ```
  It's removed from the branch tip but stays in git history, so a commit-pinned
  raw URL may still resolve — fine for our purposes.
- **Permanence:** images live as long as the repo does, and you own the repo — no
  third-party purging.
