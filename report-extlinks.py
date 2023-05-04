import os
import os.path
import sqlite3
from config import config

input = os.path.join(os.path.dirname(__file__), config['output'])
db = sqlite3.connect(input)
cur = db.cursor()

for row in cur.execute('''
SELECT url
     , status
     , filetype
     , note
  FROM contents
 WHERE url NOT LIKE 'https://jsa.gr.jp%'
   AND url NOT LIKE 'http://www.jsa.gr.jp%'
 ORDER BY url
'''):
    (url, status, filetype, note) = row
    print(f'{url}\t{status}\t{filetype}\t{note}')
