import sys
import time
import logging
from typing import List
from argparse import ArgumentParser
from datetime import timedelta
from pathlib import Path
from tqdm import tqdm
from .types import Db, TimeLimit, DEFAULT_FILE_INFO, DEFAULT_EXIF_DATA
from .sqlite import Sqlite
from .file_system import FileMetadata, walk_recurse
from .factory import Factory
from .methods.exiftool import ExifReader_Exiftool


def do():
    args = parse_arguments()

    db = Sqlite(args.database)

    if args.purge:
        logger.info('Purging database...')
        db.reset_files_data()
        db.reset_exif_data()

    if args.no_scan:
        logger.debug('Skipping file scan')
    else:
        populate_db_files(args.path, db, args.ext, args.exclude)

    collect_metadata(db, args.path, args.with_hash)

    db.close()


def populate_db_files(path: str, db: Db, filter_ext: str, exclude: List[str]):
    logger.info(f'Scanning directory {path}...')
    print('Scanning directory...')

    if filter_ext:
        filter_ext = filter_ext.lower().replace(' ', '')
        extensions = set(e if e.startswith('.') else '.' + e for e in filter_ext.split(','))
        do_filter = True
    else:
        extensions = []
        do_filter = False

    root = Path(path)
    for path in tqdm(walk_recurse(root, exclude), file=sys.stdout):
        if not do_filter or path.suffix.lower() in extensions:
            db.add_file(path)
        else:
            logger.debug(f'Ignoring due to extension filter: {path}')

    db.commit()
    logger.info(f'Directory was saved to the database')


# noinspection PyBroadException
def collect_metadata(db: Db, prefix: str, with_hash: bool):
    logger.debug('Collecting metadata...')
    print('Collecting metadata...')

    total_count = db.get_files_count(prefix)
    logger.debug(f'Found {total_count} unprocessed files')
    ExifReader_Exiftool.initialize()
    commit_strategy = TimeLimit(10.0)

    for row in tqdm(db.get_all_files(prefix), total=total_count, file=sys.stdout):
        file_id, fpath = row
        path = Path(fpath)

        try:
            fi = FileMetadata(path, with_hash).collect()
        except Exception:   # E.g. file was deleted since scan.
            fi = DEFAULT_FILE_INFO

        exif_reader = Factory.get(path.suffix)
        if exif_reader:
            er = exif_reader(path)
            try:
                exif = er.load()
                method = er.method.name
            except Exception:
                logger.exception('Error getting EXIF data')
                exif = DEFAULT_EXIF_DATA
                method = None
        else:
            exif = DEFAULT_EXIF_DATA
            method = None

        db.add_metadata(file_id, fi, exif, method)
        if commit_strategy.attempt():
            # With some storage options, committing on every iteration is very slow.
            db.commit()

        logger.info(f'Processed: {path}')

    db.commit()
    ExifReader_Exiftool.shutdown()


def parse_arguments():
    parser = ArgumentParser(prog='exif2db',
                            description='Extract metadata from the media library and store into an SQLite database.')
    parser.add_argument('path', help='Path to the media library. Content will be scanned recursively.')
    parser.add_argument('-e', '--ext', help='Filter on these file name extensions, comma-separated list.')
    parser.add_argument('-d', '--database', help='Location of SQLite database. Defaults to ./sqlite.db',
                        default='./sqlite.db')
    parser.add_argument('--purge', help='Purge the database if not empty.', action='store_true')
    parser.add_argument('--with_hash', help='Calculate SHA1 hash for each file', action='store_true')
    parser.add_argument('--no_scan', help='Do not perform new file scan (continue after a failure).',
                        action='store_true')
    parser.add_argument('-x', '--exclude', help='Exclude pattern for files and directories',
                        metavar='PATTERN', action='append')
    args = parser.parse_args()
    logger.debug(f'Arguments: {args}')

    if not Path(args.path).is_dir():
        print('Starting path must be a directory!')
        exit(1)

    return args


def main():
    start = time.monotonic()
    do()
    end = time.monotonic()
    duration = timedelta(seconds=end-start)
    print('Finished in', duration)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(filename='exif2db.log', filemode='w', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s: %(message)s')
main()
