from urllib.parse import urlparse
import os
import os.path
import sqlite3
from config import config

print('URL\tstatus\tfiletype\tnote')

parsed_start = urlparse(config['start'])
mydomains = ' AND '.join(
    map(
        lambda s : f"url NOT LIKE 'http://{s}/%' AND url NOT LIKE 'https://{s}/%'",
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
     , redirect_to
     , redirect_from
     , note
  FROM contents
 WHERE %s
 ORDER BY url
''' % mydomains):
    (url, status, filetype, redirect_to, redirect_from, note) = row
    if redirect_to:
        note = f'{note} Redirect to: {redirect_to}'
    if redirect_from:
        note = f'{note} Redirect from: {redirect_from}'
    print(f'{url}\t{status}\t{filetype}\t{note.strip()}')
