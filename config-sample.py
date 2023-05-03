config = {
    'start': 'https://example.com/',
    'domain_aliases': ['www.example.com'],
    'ignore-url': [
        'https://validator.w3.org/check',
        'https://jigsaw.w3.org/css-validator',
        '&tab_details=view&',
        '&tab_files=files&do=media',
        '?do=diff&rev',
        '?rev='
    ],
    'targeted-link-rel': [
        'stylesheet'
    ],
    'headers': {
        'User-Agent': 'bot'
    },
    'interval': 1, # seconds
    'output': 'links.sqlite'
}
