Activate Virtual Environment by Running the following command
$ . venv/bin/activate

Deactivate Virtual Environment
$ deactivate

Run Flask server by Running the following command
$ python hello.py

Run Postgres by Running the following command
$ pg_ctl -D /usr/local/var/postgres/database -l logfile start

Stop Postgres by Running the following command
$ pg_ctl -D /usr/local/var/postgres/database -l logfile stop
