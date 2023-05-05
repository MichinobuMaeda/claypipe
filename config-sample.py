config = {
    'start': 'https://example.com/',
    'domain_aliases': ['www.example.com'],
    'ignore_url': [
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
        '&rev=',
        'https://pinterest.com/pin/',
        'https://twitter.com/intent/',
        'https://www.facebook.com/sharer/',
        'https://www.googletagmanager.com/gtag/',
        'mailto:?Subject'
    ],
    'targeted_elements': {
        'a': 'href',
        'img': 'src',
        'script': 'src',
        'link': 'href',
        'iframe': 'src',
        'frame': 'src',
    },
    'targeted_link_rel': [
        'stylesheet'
    ],
    'index_files': [
        'index.html',
        'index.htm',
    ],
    'request_headers': {
        'User-Agent': 'bot'
    },
    'redirect_status': [301, 302, 303, 308],
    'interval': 1, # seconds
    'output': 'links.sqlite'
}
