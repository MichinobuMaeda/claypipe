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
     , location
  FROM contents
 WHERE url LIKE 'https://jsa.gr.jp%'
    OR url LIKE 'http://www.jsa.gr.jp%'
 ORDER BY url
'''):
    (url, status, filetype, location) = row
    print(f'{url}\t{status}\t{filetype}\t{location}')
