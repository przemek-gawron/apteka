"""Kopiuje pliki statyczne do public/, skąd Vercel serwuje je z CDN.

Flaskowe app/static na Vercelu jest ignorowane.
"""
import shutil
from pathlib import Path

src = Path("app/static")
dst = Path("public/static")
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)
