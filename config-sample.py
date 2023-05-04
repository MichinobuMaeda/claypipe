config = {
    'start': 'https://example.com/',
    'domain_aliases': ['www.example.com'],
    'ignore-url': [
        'https://php.net',
        'https://validator.w3.org/check/referer',
        'https://jigsaw.w3.org/css-validator/check/referer',
        '/wp-admin/',
        'https://dokuwiki.org/',
        'https://www.dokuwiki.org/donate',
        '/playground/',
        '/lib/exe/taskrunner.php',
        '/lib/exe/fetch.php',
        '?do=',
        '&do=',
        '?rev=',
        '&rev='
    ],
    'targeted-link-rel': [
        'stylesheet'
    ],
    'index-files': [
        'index.html',
        'index.htm',
    ],
    'headers': {
        'User-Agent': 'bot'
    },
    'interval': 1, # seconds
    'output': 'links.sqlite'
}
