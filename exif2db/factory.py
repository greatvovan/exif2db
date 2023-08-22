import logging
from typing import Type, Optional
from .types import ExifReader
from .methods.combined import ExifReader_Combined
from .methods.exiftool import ExifReader_Exiftool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Factory:
    @classmethod
    def get(cls, file_ext: str) -> Optional[Type[ExifReader]]:
        file_ext = file_ext.lower()

        if file_ext in ('.jpg', '.jpeg', '.heic', '.png', '.tiff', '.tif', '.bmp', '.crw',
                        '.gif', '.psd', '.nef'):
            if logger.level <= logging.DEBUG:
                logger.debug(f'Returning {ExifReader_Combined.__name__} for {file_ext}')
            return ExifReader_Combined

        elif file_ext in ('.orf', '.mov', '.mpg', '.mpeg', '.avi', '.mp4', '.mts', '.m2t'):
            logger.debug(f'Returning {ExifReader_Exiftool.__name__} for {file_ext}')
            return ExifReader_Exiftool

        else:
            logger.debug(f'Extension is unsupported: {file_ext}')
            return None
