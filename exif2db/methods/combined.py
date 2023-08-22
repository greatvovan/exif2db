import logging
from .pillow import ExifReader_Pillow
from .exiftool import ExifReader_Exiftool
from ..types import ExifData, ExifReader, ExifError

logger = logging.getLogger(__name__)


# noinspection PyPep8Naming
class ExifReader_Combined(ExifReader):
    def load(self) -> ExifData:
        for method in [ExifReader_Pillow, ExifReader_Exiftool]:
            er = method(self.path)
            self._method = er.method
            try:
                return er.load()
            except Exception as e:
                if method is ExifReader_Exiftool:
                    raise ExifError from e
                else:
                    logger.warning(f'{method.__name__} failed, falling back to the next method - {self.path}')
