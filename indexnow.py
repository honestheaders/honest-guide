#!/usr/bin/env python3
"""サイトマップの全URLを IndexNow で検索エンジンに知らせる。 python3 indexnow.py"""
import json, re, pathlib, urllib.request
ROOT = pathlib.Path(__file__).parent
cfg = json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
key = (ROOT/"indexnow_key.txt").read_text().strip()
urls = re.findall(r"<loc>(.*?)</loc>", (ROOT/"docs"/"sitemap.xml").read_text(encoding="utf-8"))
host = cfg["base_url"].split("//")[1].split("/")[0]
body = json.dumps({"host": host, "key": key, "keyLocation": f'{cfg["base_url"]}/{key}.txt', "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r: print("IndexNow:", r.status, len(urls), "urls")
except Exception as e: print("IndexNow error:", e)
