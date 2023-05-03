# claypipe

## Prerequisites

- Python >= 3.4

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

List broken links.

```bash
python brokenlinks.py 
```

## Create this project

Create GitHub repository with README.md, LICENSE and `.gitignore`.

```bash
git clone git@github.com:MichinobuMaeda/claypipe.git
cd claypipe
echo 3.11 > .python-version
python -m venv .venv
. .venv/bin/activate
pip install autopep8
pip install pylint
pip freeze > requirements.txt
```
