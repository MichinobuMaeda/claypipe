# claypipe

## Prerequisites

- Python >= 3.6

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

Save status of links in site pages to a Sqlite database file.

```bash
python claypipe.py
```

List results as tab delimited text files.

```bash
python report-brokenlinks.py > report-brokenlinks.log
python report-extlinks.py > report-extlinks.log
python report-sitecontents.py > report-sitecontents.log
```

## Create this project

Create GitHub repository with README.md, LICENSE and `.gitignore`.

```bash
git clone git@github.com:MichinobuMaeda/claypipe.git
cd claypipe
echo 3.6 > .python-version
python -m venv .venv
. .venv/bin/activate
pip install autopep8
pip install pylint
pip install chardet
pip freeze > requirements.txt
```
