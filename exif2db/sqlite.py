import logging
import sqlite3
import dataclasses
from pathlib import Path
from .types import Db
from .types import FileInfo, ExifData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Sqlite(Db):
    def __init__(self, filename: str):
        logger.info(f'Initializing database from {filename}...')
        self.db = sqlite3.connect(filename)

        if self.is_table_exists('files'):
            logger.debug('Table "files" exists. Getting max ID...')
            self.file_num = self.get_max_file_id()
            logger.debug(f'Got {self.file_num}')
        else:
            logger.debug('Table "files" does not exist')
            self.init_files()
            self.file_num = 0

        if self.is_table_exists('metadata'):
            logger.debug('Table "metadata" exists')
        else:
            logger.debug('Table "metadata" does not exist')
            self.init_metadata()

        self.cur = self.db.cursor()
        logger.debug('Created Sqlite instance')

    def init_files(self):
        logger.debug('Creating "files" table...')
        self.db.execute('CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, path TEXT, processed INT)')
        self.file_num = 0

    def drop_files(self):
        logger.debug('Dropping "files" table...')
        self.db.execute('DROP TABLE IF EXISTS files')

    def reset_files_data(self):
        self.drop_files()
        self.init_files()

    def init_metadata(self):
        logger.debug('Creating "metadata" table...')
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER,
                method TEXT,
                file_date_created TEXT,
                file_date_modified TEXT,
                size INTEGER,
                hash TEXT,
                mime_type TEXT,
                make TEXT,
                model TEXT,
                date_time TEXT,
                date_time_original TEXT,
                date_time_digitized TEXT,
                duration REAL,
                software TEXT,
                gps_lat REAL,
                gps_long REAL,
                gps_alt REAL,
                width INTEGER,
                height INTEGER
            )
        ''')
        self.file_num = 0

    def drop_metadata(self):
        logger.debug('Dropping "metadata" table...')
        self.db.execute('DROP TABLE IF EXISTS metadata ')

    def reset_exif_data(self):
        self.drop_metadata()
        self.init_metadata()

    def add_file(self, path: Path):
        if logger.level <= logging.DEBUG:
            logger.debug(f'Adding {path}...')

        self.file_num += 1
        self.cur.execute('INSERT INTO files VALUES (?, ?, ?)', (self.file_num, str(path), 0))

    def add_metadata(self, file_id: int, fi: FileInfo, exif: ExifData, method: str):
        if logger.level <= logging.DEBUG:
            logger.debug(f'Adding metadata for file ID {file_id}...')

        self.cur.execute('INSERT INTO metadata VALUES '
                         '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         (file_id, method) + dataclasses.astuple(fi) + dataclasses.astuple(exif))
        self.cur.execute('UPDATE files SET processed = 1 WHERE id = ?', (file_id,))

    def commit(self):
        logger.debug("Committing...")
        self.db.commit()

    def close(self):
        logger.debug('Closing database...')
        self.db.close()

    def get_all_files(self, prefix: str):
        logger.debug(f'Retrieving unprocessed files under {prefix}...')
        return self.db.execute('SELECT id, path FROM files WHERE processed = 0 and path LIKE ?', (prefix + '%',))

    def get_files_count(self, prefix: str):
        logger.debug('Retrieving files count...')
        cur = self.db.execute('SELECT count(*) FROM files WHERE processed = 0 and path LIKE ?', (prefix + '%',))
        return cur.fetchone()[0]

    def is_table_exists(self, table: str):
        res = self.db.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)).fetchone()
        return bool(res)

    def get_max_file_id(self):
        return self.db.execute('SELECT max(id) FROM files').fetchone()[0]
