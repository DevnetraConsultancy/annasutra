import re
from pathlib import Path

emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]|[\ufe0f]')

def audit_html(filepath):
    p = Path(filepath)
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    print(f"\n==========================================")
    print(f"AUDITING: {filepath}")
    matches = emoji_pattern.findall(text)
    print(f"Total emojis: {len(matches)}")
    print(f"Unique emojis: {[hex(ord(c)) for c in set(matches)]}")
    for idx, line in enumerate(lines, 1):
        if emoji_pattern.search(line):
            safe = line.strip().encode('ascii', 'backslashreplace').decode('ascii')
            print(f"  L{idx:4d}: {safe[:90]}")

audit_html('backend/apps/publicview/templates/publicview/landing.html')
