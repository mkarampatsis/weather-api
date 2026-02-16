#!/usr/bin/env python3
import re
import json
import sys
from pathlib import Path


def main():
    src = Path('weather_data.json')
    dst = Path('weather_data_fixed.json')
    if not src.exists():
        print('Source file not found:', src)
        sys.exit(1)
    text = src.read_text(encoding='utf-8')

    # Replace pandas Timestamp(...) with the inner string
    text = re.sub(r"Timestamp\('([^']+)'\s*,\s*tz='[^']+'\)", r'"\1"', text)

    # Replace Python bytes notation b'..' with plain strings
    text = re.sub(r"b'([^']*)'", r'"\1"', text)

    # Convert single-quoted strings to double-quoted JSON strings
    text = text.replace("'", '"')

    # Optional: remove trailing Python-style commas before closing brackets (rare)
    text = re.sub(r",\s*(\]|\})", r"\1", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print('JSON decode error:', e)
        # Save the transformed text for debugging
        debug = Path('weather_data_transformed.txt')
        debug.write_text(text, encoding='utf-8')
        print('Wrote transformed text to', debug)
        sys.exit(2)

    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Wrote fixed JSON to', dst)


if __name__ == '__main__':
    main()
