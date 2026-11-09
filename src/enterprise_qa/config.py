"""Minimal literal .env loader: no shell execution or interpolation."""
import os
import re
from pathlib import Path

ALLOWED = {"DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "DEEPSEEK_BASE_URL", "SILICONFLOW_API_KEY", "SILICONFLOW_MODEL", "SILICONFLOW_BASE_URL"}

def load_env(path=".env"):
    file = Path(path)
    if not file.exists():
        return
    pending = {}
    for number, raw in enumerate(file.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, sep, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"Invalid .env syntax on line {number}")
        if value.startswith((chr(34), chr(39))):
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError(f"Unclosed .env quote on line {number}")
            value = value[1:-1]
        if key in ALLOWED:
            pending[key] = value
    for key, value in pending.items():
        os.environ.setdefault(key, value)
