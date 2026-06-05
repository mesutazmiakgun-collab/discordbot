import re
from pathlib import Path
from collections import Counter
path = Path('bot.py')
text = path.read_text(encoding='utf-8')
names = re.findall(r"@bot\.tree\.command\(name=['\"]([^'\"]+)['\"]", text)
print('count', len(names))
print('dups', {k:v for k,v in Counter(names).items() if v>1})
print('invalid', [n for n in names if not re.match(r'^[a-z0-9_-]{1,32}$', n)])
