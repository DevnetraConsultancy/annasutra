import re
from pathlib import Path

emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]|[\ufe0f]')

for filename in ['lot_summary.html', 'lot_not_found.html']:
    p = Path(f'backend/apps/publicview/templates/publicview/{filename}')
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    print(f"\nAUDITING {filename}:")
    for idx, line in enumerate(lines, 1):
        if emoji_pattern.search(line):
            safe = line.strip().encode('ascii', 'backslashreplace').decode('ascii')
            print(f"  L{idx:4d}: {safe[:100]}")
