import logging
from typing import Optional
from PIL import Image
from PIL.ExifTags import Base, GPS, IFD
from PIL.TiffImagePlugin import IFDRational
from pi_heif import register_heif_opener
import pillow_avif
from ..types import ExifData, ExifReader, Method, DEFAULT_EXIF_DATA
from ..utils import dms2dd, parse_exif_date

register_heif_opener()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# noinspection PyPep8Naming
class ExifReader_Pillow(ExifReader):
    method = Method.Pillow

    def load(self) -> ExifData:
        # noinspection PyBroadException
        try:
            if logger.level <= logging.DEBUG:
                logger.debug(f'Opening {self.path}...')

            img = Image.open(self.path)
            logger.debug('Getting EXIF data...')

            exif = img.getexif()

            if exif:
                logger.debug('Got EXIF data')
                exif_exif = exif.get_ifd(IFD.Exif)
                exif_gps = exif.get_ifd(IFD.GPSInfo)

                date_time = exif.get(Base.DateTime)
                date_time_original = exif_exif.get(Base.DateTimeOriginal)
                date_time_digitized = exif_exif.get(Base.DateTimeDigitized)
                date_time_sub_sec = exif.get(Base.SubsecTime)
                date_time_original_sub_sec = exif_exif.get(Base.SubsecTimeOriginal)
                date_time_digitized_sub_sec = exif_exif.get(Base.SubsecTimeDigitized)

                lat = exif_gps.get(GPS.GPSLatitude)
                long = exif_gps.get(GPS.GPSLongitude)
                alt = exif_gps.get(GPS.GPSAltitude)

                return ExifData(
                    'image/' + img.format.lower(),
                    exif.get(Base.Make),
                    exif.get(Base.Model),
                    parse_exif_date(date_time, date_time_sub_sec),
                    parse_exif_date(date_time_original, date_time_original_sub_sec),
                    parse_exif_date(date_time_digitized, date_time_digitized_sub_sec),
                    None,
                    exif.get(Base.Software),
                    self._parse_coordinate(lat, exif_gps.get(GPS.GPSLatitudeRef)),
                    self._parse_coordinate(long, exif_gps.get(GPS.GPSLongitudeRef)),
                    float(alt) if alt else None,
                    exif_exif.get(Base.ExifImageWidth),
                    exif_exif.get(Base.ExifImageHeight),
                )
            else:
                logger.debug('EXIF data was not found')
                return DEFAULT_EXIF_DATA
        except Exception:
            logger.exception(f'Pillow error for {self.path}')
            raise

    @staticmethod
    def _parse_coordinate(c, ref: str) -> Optional[float]:
        if c is None or ref is None:
            return None

        if type(c) is tuple:
            return dms2dd(c[0], c[1], c[2], ref)

        if type(c) is IFDRational:
            res = float(c)
            if ref in ('S', 'W'):
                res = -res
            return res

        logger.warning('Unexpected EXIF GPS content')
        return None
