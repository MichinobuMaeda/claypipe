import os, re, ssl, sys, traceback, time
from datetime import datetime
from http.client import HTTPSConnection, HTTPConnection
from html.parser import HTMLParser
from urllib.parse import urlparse, quote
import mimetypes
import sqlite3
import chardet
from config import config

class HTMLLinkParser(HTMLParser):
    def __init__(self, ignoreurl, linkrels):
        super().__init__()
        self.links = []
        self.ignoreurl = ignoreurl
        self.linkrels = linkrels

    def handle_starttag(self, tag, attrs):
        for (key, val) in attrs:
            if tag.lower() == 'link' and key.lower() == 'rel':
                if not val.lower() in self.linkrels:
                    return

        for (key, val) in attrs:
            if (
                (tag.lower() == 'a' and key.lower() == 'href') or
                (tag.lower() == 'img' and key.lower() == 'src') or
                (tag.lower() == 'script' and key.lower() == 'src') or
                (tag.lower() == 'link' and key.lower() == 'href') or
                (tag.lower() == 'iframe' and key.lower() == 'src') or
                (tag.lower() == 'frame' and key.lower() == 'src')
            ):
                for item in self.ignoreurl:
                    if item in val:
                        return

                self.links.append(val.strip())

class Content:
    def __init__(self, target, base=None):
        url = re.sub('#.*', '', target)

        if url.startswith('http://') or url.startswith('https://'):
            self.url = url
        elif url.startswith('//'):
            self.url = f'{base.scheme}:{url}'
        elif url.startswith('/'):
            self.url = f'{base.scheme}://{base.netloc}{url}'
        else:
            self.url = f'{base.scheme}://{base.netloc}{base.parent}/{url}'
            while (re.search('\/\.\/', self.url)):
                self.url = re.sub('\/\.\/', '/', self.url)

            while (re.search('\/[^/]+\/\.\.\/', self.url)):
                self.url = re.sub('\/[^/]+\/\.\.\/', '/', self.url)

        parsed = urlparse(self.url)
        self.scheme = parsed.scheme
        self.netloc = parsed.netloc
        self.path = quote(parsed.path)
        self.parent = quote(re.sub('\/[^/]*$', '', self.path))
        self.hostname = parsed.hostname
        self.port = parsed.port
        self.filetype = ''
        self.status = 0
        self.redirect_to = ''
        self.redirect_from = ''
        self.note = ''
        self.links = []

        if self.path != parsed.path:
            self.note = self.url
            self.url = self.url.replace(parsed.path, self.path)

        if self.path == '':
            self.url = f'{self.url}/'
            self.path = '/'
            self.parent = ''

        if self.path.endswith('/'):
            self.filetype = 'html'
        else:
            guessed = mimetypes.guess_type(self.path)
            mimetype = guessed[0]
            if mimetype:
                ext = mimetypes.guess_extension(mimetype)
                if ext:
                    self.filetype = ext[1:]

    def request(self, methd, headers):
        try:
            if self.scheme == 'https':
                context = ssl.create_default_context()
                conn = HTTPSConnection(
                    self.hostname,
                    port=self.port,
                    context=context
                )
            else:
                conn = HTTPConnection(
                    self.hostname,
                    port=self.port,
                )
            conn.request(methd, url=self.url, headers=headers)
            return conn.getresponse()
        except ssl.SSLCertVerificationError:
            self.note = 'Error: SSL Cert verification'
            return None
        except:
            traceback.print_exc(file=sys.stdout)
            return None
    
    def retrieve(self, interval, domains, headers, ignoreurl, rels, indexfiles):
        if self.status:
            return

        time.sleep(interval / 10)
        resp = self.request('HEAD', headers)

        if not resp:
            return

        self.status = resp.status

        if self.status in [301, 302, 303, 308]:
            if 'Location' in resp.headers:
                self.redirect_to = resp.headers['Location']

        if self.status != 200:
            return

        if not self.filetype:
            if 'Content-Type' in resp.headers:
                mimetype = resp.headers['Content-Type']
                mimetype = re.sub(';.*', '', mimetype)
                if mimetype:
                    ext = mimetypes.guess_extension(mimetype)
                    if ext:
                        self.filetype = ext[1:]
        
        if self.filetype != 'html':
            return
        
        if not self.hostname in domains:
            return

        time.sleep(interval)
        resp = self.request('GET', headers)

        if not resp:
            return

        self.status = resp.status

        data = resp.read()
        enc = chardet.detect(data)['encoding']

        if not enc:
            return

        parser = HTMLLinkParser(ignoreurl, rels)
        parser.feed(data.decode(enc, errors='ignore'))
        urls = []

        for link in parser.links:
            if link in indexfiles:
                link = ''
            else:
                filename = re.sub('.*\/', '', re.sub('[#].*', '', link))
                directory = re.sub('\/[^/]*$', '/', re.sub('[#?].*', '', link))

                if filename in indexfiles:
                    link = directory

            content = Content(link, base=self)

            if content.url in urls:
                continue

            urls.append(content.url)
            self.links.append(content)

class Crawler:
    def __init__(self, start, db, domains, headers,
                 interval, ignoreurl, linkrels, indexfiles):
        self.start = start
        self.urls = [self.start.url]
        self.contents = [self.start]
        self.db = db
        self.domains = domains
        self.headers = headers
        self.interval = interval
        self.ignoreurl = ignoreurl
        self.linkrels = linkrels
        self.indexfiles = indexfiles

    def addlink(self, db, target, page=None):
        if target.url in self.urls:
            return

        self.urls.append(target.url)
        self.contents.append(target)

        try:
            cur = db.cursor()
            cur.execute('''
INSERT OR IGNORE INTO contents (
       url
) VALUES (
       ?
)
''',
                [target.url]
            )
            db.commit()
        except:
            print(target.url)
            traceback.print_exc(file=sys.stdout)

        if not page:
            return

        try:
            cur = self.db.cursor()
            cur.execute('''
INSERT OR IGNORE INTO links (
       page
     , link
) VALUES (
       (SELECT id FROM contents WHERE url = ?)
     , (SELECT id FROM contents WHERE url = ?)
)
''',
                (page.url, target.url)
            )
            self.db.commit()
        except:
            print(page.path, target.url)
            traceback.print_exc(file=sys.stdout)

    def retrieve(self, content):
        content.retrieve(self.interval, self.domains, self.headers,
                         self.ignoreurl, self.linkrels, self.indexfiles)
        print(f'{content.url}\t{content.status}\t{content.filetype}\t{content.note}')

        if content.status in [301, 302, 303, 308]:
            if content.redirect_to:
                target = Content(content.note, content)
                target.redirect_from = content.url
                self.addlink(db, target)

        try:
            cur = self.db.cursor()
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
            self.db.commit()
        except:
            traceback.print_exc(file=sys.stdout)
        
        for target in content.links:
            self.addlink(db, target, content)
    
    def crawl(self):
        while len(self.contents):
            content = self.contents.pop(0)
            self.retrieve(content)

def initdb(path):
    if os.path.exists(path):
        ut = datetime.fromtimestamp(os.path.getmtime(path))
        ts = ut.strftime("%Y%m%d%H%M%S")
        bak = re.sub('\.', f'_{ts}.', path)
        os.rename(path, bak)

    open(path, 'a').close()
    db = sqlite3.connect(path)
    cur = db.cursor()
    # SQLite's soecification:
    #   INTEGER PRIMARY KEY is ROWID.
    #   ROWID is auto inclement number.
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
    # Table "links" represents N:N relationship between pages and links.
    cur.execute('''
CREATE TABLE links (
       page             INTEGER
     , link             INTEGER
     , PRIMARY KEY (page, link)
) WITHOUT ROWID
''')
    return db

if __name__ == '__main__':
    start = Content(config['start'])
    db = initdb(os.path.join(os.path.dirname(__file__), config['output']))

    cur = db.cursor()
    cur.execute('''
INSERT OR IGNORE INTO contents (
       url
) VALUES (
       ?
)
''',
        [config['start']]
    )
    db.commit()

    crawler = Crawler(
        Content(config['start']),
        db,
        [start.hostname] + config['domain_aliases'],
        config['headers'],
        config['interval'],
        config['ignore-url'],
        config['targeted-link-rel'],
        config['index-files']
    )

    crawler.crawl()
