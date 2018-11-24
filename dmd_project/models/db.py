import os
import psycopg2
import psycopg2.extras


def connect_to_db():
    db_port = int(os.environ.get('DB_PORT', 6060))
    db_host = os.environ.get('DB_HOST', 'localhost')

    connection = psycopg2.connect(
        'dbname=dmd_project '
        'user=dmd_project '
        f'host={db_host} '
        f'port={db_port} '
        'password=dmd_project'
    )
    return connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
