import logging
import hashlib
from typing import List
from pathlib import Path
from datetime import datetime
from fnmatch import fnmatch
from .types import FileInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def walk_recurse(root: Path, exclude: List[str]):
    """Process files first and directories later."""

    dirs = []
    if logger.level <= logging.DEBUG:
        logger.debug(f'Scanning {root}...')

    contents = sorted(root.iterdir())
    if logger.level <= logging.DEBUG:
        logger.debug(f'{len(contents)} child elements found')

    for el in contents:
        if el.is_file() and not _is_excluded(el.name, exclude):
            yield el
        if el.is_dir() and not el.is_symlink() and not _is_excluded(el.name, exclude):
            dirs.append(el)

    dirs = sorted(dirs)
    if logger.level <= logging.DEBUG:
        logger.debug(f'{len(dirs)} directories found')

    for d in dirs:
        yield from walk_recurse(d, exclude)


def _is_excluded(name: str, exclude: List[str]):
    if not exclude:
        return False

    for pattern in exclude:
        if fnmatch(name, pattern):
            return True

    return False


class FileMetadata:
    def __init__(self, path: Path, with_hash: bool):
        self.path = path
        self.with_hash = with_hash

    def collect(self) -> FileInfo:
        if logger.level <= logging.DEBUG:
            logger.debug(f'Getting file system info for {self.path}...')

        stat = self.path.stat()

        if self.with_hash:
            hash_hex = self.get_hash()
        else:
            hash_hex = None

        logger.debug('Done')
        return FileInfo(
            datetime.fromtimestamp(stat.st_ctime),
            datetime.fromtimestamp(stat.st_mtime),
            stat.st_size,
            hash_hex,
        )

    def get_hash(self) -> str:
        logger.debug('Calculating hash...')
        buff_size = 2**20 * 4
        alg = hashlib.sha1()

        with open(self.path, 'rb') as f:
            while True:
                data = f.read(buff_size)
                if not data:
                    break

                alg.update(data)

        return alg.hexdigest()
