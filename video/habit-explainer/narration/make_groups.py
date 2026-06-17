"""SRT(ch1-5) を章オフセットでシフトし、index.html 埋め込み用 GROUPS JS配列を出力する。"""
import re, json, pathlib

DIR = pathlib.Path(__file__).parent
OFFSETS = {1: 1.0, 2: 50.85, 3: 98.47, 4: 145.95, 5: 195.37}

def parse_ts(ts):
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

groups = []
for ch, off in OFFSETS.items():
    text = (DIR / f"ch{ch}.srt").read_text(encoding="utf-8-sig")
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        if len(lines) < 3:
            continue
        m = re.match(r"([\d:,]+)\s*-->\s*([\d:,]+)", lines[1])
        start = round(parse_ts(m.group(1)) + off, 2)
        end = round(parse_ts(m.group(2)) + off, 2)
        groups.append({"s": start, "e": end, "t": "".join(lines[2:])})

for i in range(1, len(groups)):
    if groups[i]["s"] < groups[i - 1]["e"]:
        groups[i - 1]["e"] = groups[i]["s"]

print("var GROUPS = [")
for g in groups:
    print(f'  {{s:{g["s"]},e:{g["e"]},t:{json.dumps(g["t"], ensure_ascii=False)}}},')
print("];")
print(f"// {len(groups)} groups, last end = {groups[-1]['e']}")
