import re
from pathlib import Path

emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]|[\ufe0f]')

def audit_file(filepath):
    p = Path(filepath)
    if not p.exists():
        print(f"File not found: {filepath}")
        return
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    print(f"\n==========================================")
    print(f"AUDITING: {filepath}")
    print(f"Total lines: {len(lines)}")
    matches = emoji_pattern.findall(text)
    print(f"Total emojis found: {len(matches)}")
    print(f"Unique emojis: {[hex(ord(c)) for c in set(matches)]}")
    print(f"Sample matches:")
    for idx, line in enumerate(lines, 1):
        if emoji_pattern.search(line):
            safe = line.strip().encode('ascii', 'backslashreplace').decode('ascii')
            print(f"  L{idx:4d}: {safe[:100]}")

audit_file('backend/apps/publicview/static/publicview/js/annasutra_i18n.js')
audit_file('backend/apps/publicview/static/publicview/js/producer_wizard.js')
