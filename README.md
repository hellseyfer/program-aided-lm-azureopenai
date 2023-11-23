## if you need the DB, these are the steps you need to proceed:
# create db Chinook
sqlite3 Chinook.db
# run sql script
.read Chinobook.sql
# test db
SELECT * FROM Artist LIMIT 10;
