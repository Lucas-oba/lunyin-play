#!/usr/bin/env python3
import base64, gzip, hashlib, json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
out.mkdir(parents=True, exist_ok=True)

text_files = [
    "index.html",
    "index.js",
    "index.audio.worklet.js",
    "index.audio.position.worklet.js",
    "README.md",
]
for name in text_files:
    (out / name).write_bytes((root / name).read_bytes())
(out / ".nojekyll").write_text("")

manifest = json.loads((root / "manifest.json").read_text())
for item in manifest:
    b64 = "".join((root / part).read_text() for part in item["parts"])
    payload = base64.b64decode(b64)
    raw = gzip.decompress(payload) if item["gzip"] else payload
    digest = hashlib.sha256(raw).hexdigest()
    if digest != item["sha256"] or len(raw) != item["raw_size"]:
        raise SystemExit(
            f"checksum fail {item['name']}: got {digest} size {len(raw)}"
        )
    (out / item["name"]).write_bytes(raw)
    print("ok", item["name"], len(raw), digest)

print("decoded into", out)
