from urllib.parse import urlparse
import os
import os.path
import sqlite3
from config import config

print('URL\tstatus\tfiletype\tnote')

parsed_start = urlparse(config['start'])
mydomains = ' OR '.join(
    map(
       lambda s : f"url LIKE 'http://{s}/%' OR url LIKE 'https://{s}/%'",
       [parsed_start.hostname] + config['domain_aliases']
    )
)

input = os.path.join(os.path.dirname(__file__), config['output'])
db = sqlite3.connect(input)
cur = db.cursor()

for row in cur.execute('''
SELECT url
     , status
     , filetype
     , note
  FROM contents
 WHERE %s
 ORDER BY url
''' % mydomains):
    (url, status, filetype, note) = row
    print(f'{url}\t{status}\t{filetype}\t{note}')
