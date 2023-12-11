## if you need the DB, these are the steps you need to proceed:

### create db Chinook

sqlite3 Chinook.db

### run sql script

.read Chinobook.sql

### test db

SELECT \* FROM Artist LIMIT 10;

### MacOS installation

in MacOs you must change tensorflow for tensorflow-mac in Pipfile and install all dependencies with pipenv install --dev


## initialize server (refactor-pandora-ai)
go to refactor-pandora-ai/server and write this command:
uvicorn main:app --reload