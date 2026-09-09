#!/usr/bin/env python3
"""Pull live pricing for Phosphors CRT from the App Store and write it into the site.

Sources, US storefront:
  - iTunes lookup API (JSON): the app's own price and current version.
  - The App Store web page (HTML): in-app purchase prices, which the lookup
    API does not expose. Parsed from the embedded JSON the page ships with.

Writes assets/data/store.json and rewrites every element in index.html
carrying a data-store="<key>" attribute, plus the JSON-LD offer price.

Exits non-zero if any value cannot be parsed, so the GitHub Action never
commits a half-updated page. Run with --check to fetch and report without
writing.
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

APP_ID = "6784439481"
STOREFRONT = "us"
IAP_NAME = "Phosphors Pro"

LOOKUP_URL = f"https://itunes.apple.com/lookup?id={APP_ID}&country={STOREFRONT}"
STORE_URL = f"https://apps.apple.com/{STOREFRONT}/app/phosphors-crt/id{APP_ID}?mt=12"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
DATA = ROOT / "assets" / "data" / "store.json"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def app_info() -> dict:
    payload = json.loads(fetch(LOOKUP_URL))
    if payload.get("resultCount") != 1:
        raise RuntimeError(f"lookup returned {payload.get('resultCount')} results")
    r = payload["results"][0]
    return {
        "app_price": r["formattedPrice"],   # "Free" or "$4.99"
        "app_price_number": r["price"],     # 0.0
        "version": r["version"],
        "minimum_os": r["minimumOsVersion"],
    }


def iap_price(html: str) -> str:
    # The page embeds its data as JSON; the IAP list appears as
    # {"leadingText":"Phosphors Pro","trailingText":"$9.99"} and, older
    # shape, as ["Phosphors Pro","$9.99"]. Accept either.
    name = re.escape(IAP_NAME)
    patterns = [
        rf'"leadingText"\s*:\s*"{name}"\s*,\s*"trailingText"\s*:\s*"([^"]+)"',
        rf'\[\s*"{name}"\s*,\s*"([^"]+)"\s*\]',
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            return m.group(1)
    raise RuntimeError(f'in-app purchase "{IAP_NAME}" not found on store page')


def rewrite_index(values: dict) -> bool:
    html = INDEX.read_text(encoding="utf-8")
    original = html
    for key, value in values.items():
        if "-" not in key:
            continue  # only data-store keys, not the numeric offer price
        pattern = rf'(<span data-store="{re.escape(key)}">)[^<]*(</span>)'
        html, n = re.subn(pattern, rf"\g<1>{value}\g<2>", html)
        if n == 0:
            print(f"warning: no data-store=\"{key}\" element in index.html", file=sys.stderr)
    # JSON-LD offer for the app itself.
    html = re.sub(
        r'("@type":\s*"Offer",\s*"price":\s*")[^"]*(")',
        rf"\g<1>{values['app_price_number']:g}\g<2>",
        html,
    )
    if html != original:
        INDEX.write_text(html, encoding="utf-8")
        return True
    return False


def main() -> int:
    check_only = "--check" in sys.argv

    info = app_info()
    page = fetch(STORE_URL).decode("utf-8", errors="replace")
    pro = iap_price(page)

    values = {
        "app-price": info["app_price"],
        "pro-price": pro,
        "version": info["version"],
        "app_price_number": info["app_price_number"],
    }
    record = {
        "app_id": APP_ID,
        "storefront": STOREFRONT,
        "app_price": info["app_price"],
        "pro_price": pro,
        "pro_name": IAP_NAME,
        "version": info["version"],
        "minimum_os": info["minimum_os"],
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    print(json.dumps(record, indent=2))
    if check_only:
        return 0

    changed = rewrite_index(values)

    # Only rewrite the JSON when a value moved, so the daily run does not
    # produce a commit that changes nothing but a timestamp.
    previous = json.loads(DATA.read_text()) if DATA.exists() else {}
    stable = {k: v for k, v in record.items() if k != "fetched_at"}
    prev_stable = {k: v for k, v in previous.items() if k != "fetched_at"}
    if stable != prev_stable:
        DATA.parent.mkdir(parents=True, exist_ok=True)
        DATA.write_text(json.dumps(record, indent=2) + "\n")
        changed = True

    print("updated" if changed else "no change")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - report and fail the job
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
