import os, re, ssl, sys, traceback, time
from datetime import datetime
from http.client import HTTPSConnection, HTTPConnection
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit, urljoin, quote_plus
import mimetypes
import sqlite3
import chardet
from config import config

def strip_index(url, indexfiles):
    (scheme, netloc, path, query, fragment) = urlsplit(url)

    for name in indexfiles:
        path = re.sub(f'\/{name}$', '/', path)

    return urlunsplit((scheme, netloc, path, query, fragment))

def full_url(page, link):
    url = urljoin(page, re.sub('#.*', '', link.strip()))
    return f'{url}/' if urlsplit(url).path == '' else url

def guess_filetype(url, resp=None):
    if url.endswith('/'):
        return 'html'

    mimetype = mimetypes.guess_type(url)[0]

    if not mimetype:
        if resp and resp.headers and 'Content-Type' in resp.headers:
            mimetype = re.sub(';.*', '', resp.headers['Content-Type'])

    if not mimetype:
        return ''

    ext = mimetypes.guess_extension(mimetype)
    return ext[1:] if ext else ''

def request(methd, url, headers):
    try:
        parsed = urlsplit(url)
        conn = HTTPSConnection(
                parsed.hostname,
                port=parsed.port,
                context=ssl.create_default_context()
            ) if parsed.scheme == 'https' else HTTPConnection(
                parsed.hostname,
                port=parsed.port,
            )
        conn.request(methd, url=quote_plus(url, '/:?=&@'), headers=headers)
        return (conn.getresponse(), None)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return (None, type(e).__name__)

def initdb(relative_path):
    path = os.path.join(os.path.dirname(__file__), relative_path)

    try:
        if os.path.exists(path):
            ts = os.path.getmtime(path)
            suffix = datetime.fromtimestamp(ts).strftime("%Y%m%d%H%M%S")
            os.rename(path, re.sub('\.', f'_{suffix}.', path))

        # Create an empty file
        open(path, 'a').close()

        db = sqlite3.connect(path)
        cur = db.cursor()

        # SQLite's spec.: INTEGER PRIMARY KEY is auto-inclement ROWID.
        cur.execute('''
CREATE TABLE contents (
       id               INTEGER PRIMARY KEY
     , url              TEXT UNIQUE
     , status           INTEGER NOT NULL DEFAULT 0
     , filetype         TEXT NOT NULL DEFAULT ''
     , redirect_to      TEXT NOT NULL DEFAULT ''
     , redirect_from    TEXT NOT NULL DEFAULT ''
     , note             TEXT NOT NULL DEFAULT ''
)
''')

        # N:N relationship between pages and links.
        cur.execute('''
CREATE TABLE links (
       page             INTEGER
     , link             INTEGER
     , PRIMARY KEY (page, link)
) WITHOUT ROWID
''')
    except:
        traceback.print_exc(file=sys.stderr)

    return db

def add_content(db, urls, contents, content):
    if content.url in urls:
        return

    urls.append(content.url)
    contents.append(content)

    try:
        cur = db.cursor()
        cur.execute('''
INSERT OR IGNORE INTO contents (
       url
) VALUES (
       ?
)
''',
            [content.url]
        )
        db.commit()
    except:
        traceback.print_exc(file=sys.stderr)

def add_link(db, page, link):
    try:
        cur = db.cursor()
        cur.execute('''
INSERT OR IGNORE INTO links (
       page
     , link
) VALUES (
       (SELECT id FROM contents WHERE url = ?)
     , (SELECT id FROM contents WHERE url = ?)
)
''',
            (page.url, link.url)
        )
        db.commit()
    except:
        traceback.print_exc(file=sys.stderr)

def save_content(db, urls, contents, content):        
    print(f'{content.url}\t{content.status}\t{content.filetype}\t{content.note}')

    for target in content.links:
        add_content(db, urls, contents, target)
        add_link(db, content, target)

    try:
        cur = db.cursor()
        cur.execute('''
UPDATE contents
   SET status = ?
     , filetype = ?
     , redirect_to = ?
     , redirect_from = ?
     , note = ?
 WHERE url = ?
''',
            (content.status, content.filetype,
                content.redirect_to, content.redirect_from, content.note,
                content.url)
        )
        db.commit()
    except:
        traceback.print_exc(file=sys.stderr)

class Content:
    def __init__(self, url):
        self.url = url
        self.status = 0
        self.redirect_to = ''
        self.redirect_from = ''
        self.note = ''
        self.links = []
        self.filetype = guess_filetype(url)

class LinkParser(HTMLParser):
    def __init__(self, link_hander):
        super().__init__()
        self.link_hander = link_hander

    def handle_starttag(self, tag, attrs):
        self.link_hander(tag, attrs)

def link_hander(tag, attrs, page,
                ignoreurl, elements, linkrels, link_to_url):
    if not tag.lower() in elements:
        return

    if tag.lower() == 'link':
        for (name, val) in attrs:
            if name.lower() == 'rel' and (not name.lower() in linkrels):
                return

    for (name, val) in attrs:
        if name.lower() != elements[tag.lower()]:
            continue

        for item in ignoreurl:
            if item in val:
                return

        url = link_to_url(page, val)

        if url in page.links:
            return

        page.links.append(Content(url))

def retrieve_content(db, urls, contents, content,
             domains, interval, redirectstatus,
             request, link_to_url, link_parser):
    time.sleep(interval / 10)
    (resp, err) = request('HEAD', content.url)

    if not resp:
        content.note = err if err else 'Unknown error'
        return content

    content.status = resp.status

    if content.status in redirectstatus and 'Location' in resp.headers:
        content.redirect_to = resp.headers['Location']
        target = Content(link_to_url(content, content.redirect_to))
        target.redirect_from = content.url
        add_content(db, urls, contents, target)

    if content.status != 200:
        return content        

    content.filetype = guess_filetype(content.url, resp)

    if content.filetype != 'html':
        return content

    if not urlsplit(content.url).hostname in domains:
        return content

    time.sleep(interval)
    (resp, err) = request('GET', content.url)

    if not resp:
        return content

    content.status = resp.status
    data = resp.read()
    enc = chardet.detect(data)['encoding']

    if not enc:
        return content

    link_parser(content, data.decode(enc, errors='ignore'))
    return content

if __name__ == '__main__':
    urls = []
    contents = []
    db = initdb(config['output'])
    target = Content(config['start'])
    add_content(db, urls, contents, target)

    link_to_url = lambda page, link: strip_index(
        full_url(page.url, link), config['index_files']
    )

    link_parser = lambda page, html: LinkParser(
        lambda tag, attrs: link_hander(
            tag, attrs, page,
            config['ignore_url'],
            config['targeted_elements'],
            config['targeted_link_rel'],
            link_to_url
        )
    ).feed(html)

    while len(contents):
        save_content(
            db, urls, contents,
            retrieve_content(
                db, urls, contents,
                contents.pop(0),
                [urlsplit(target.url).hostname] + config['domain_aliases'],
                config['interval'],
                config['redirect_status'],
                lambda methd, url: request(methd, url, config['request_headers']),
                link_to_url,
                link_parser
            )
        )
