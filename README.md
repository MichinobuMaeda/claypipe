# claypipe

Link checker

## Prerequisites

- Python >= 3.8

## Usage

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Copy and edit `config.py`.

```bash
cp config-sample.py config.py
```

Save status of links in your site pages to a SQLite database file: `links.sqlite`.

```bash
python claypipe.py
```

List results as tab delimited text files.

```bash
python report-pages.py > report-pages.log
python report-extlinks.py > report-extlinks.log
python report-sitecontents.py > report-sitecontents.log
```

## Appndix: Create this project

Create GitHub repository with `README.md`, `LICENSE` (MIT) and `.gitignore` (Python).

```bash
git clone git@github.com:MichinobuMaeda/claypipe.git
cd claypipe
echo 3.8 > .python-version
python -m venv .venv
. .venv/bin/activate
pip install autopep8
pip install pylint
pip install chardet
pip install pip-upgrader
pip freeze > requirements.txt
```
