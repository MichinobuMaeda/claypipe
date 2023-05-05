import os
import os.path
import sqlite3
from config import config

print('link\tpage\tstatus')

input = os.path.join(os.path.dirname(__file__), config['output'])
db = sqlite3.connect(input)
cur = db.cursor()

for row in cur.execute('''
SELECT (SELECT c1.url FROM contents as c1 WHERE c1.id = l.link)
     , (SELECT c2.url FROM contents as c2 WHERE c2.id = l.page)
     , c.status
  FROM links as l
  LEFT JOIN contents as c
    ON c.id = l.link
 WHERE NOT c.status IN (200, 304, 401, 402)
 ORDER BY l.link, l.page
'''):
    (link, page, status) = row
    print(f'{link}\t{page}\t{status}')
