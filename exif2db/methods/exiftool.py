import logging
from exiftool import ExifToolHelper
from ..types import ExifData, ExifReader, Method, DEFAULT_EXIF_DATA
from ..utils import parse_exif_date

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# noinspection PyPep8Naming
class ExifReader_Exiftool(ExifReader):
    method = Method.Exiftool
    tags = []
    process: ExifToolHelper = None

    @classmethod
    def initialize(cls):
        logger.debug('Launching process...')
        cls.process = ExifToolHelper()

    @classmethod
    def shutdown(cls):
        logger.debug('Stopping process...')
        cls.process.terminate()

    def load(self) -> ExifData:
        et = self.process   # Brevity only

        if logger.level <= logging.DEBUG:
            logger.debug(f'Getting EXIF data from {self.path}...')

        for metadata_dict in et.get_metadata(self.path):
            logger.debug('Got EXIF data')

            # See https://exiftool.org/TagNames/EXIF.html
            mime_type, mime_subtype = metadata_dict.get('File:MIMEType').split('/')
            if mime_type == 'image':
                return self._from_image(metadata_dict)
            elif mime_type == 'video':
                if mime_subtype == 'quicktime':
                    return self._from_video_quicktime(metadata_dict)
                elif mime_subtype == 'm2ts':
                    return self._from_video_m2ts(metadata_dict)
                elif mime_subtype == 'mp4':
                    return self._from_video_mp4(metadata_dict)
                elif mime_subtype == 'mpeg':
                    return self._from_video_mpg(metadata_dict)
                elif mime_subtype == 'x-msvideo':
                    return self._from_video_avi(metadata_dict)
        else:
            logger.debug(f'Unsupported MIME type for {self.path}')

        return DEFAULT_EXIF_DATA

    @staticmethod
    def _from_image(d: dict) -> ExifData:
        date_time = d.get('EXIF:ModifyDate')
        date_time_original = d.get('EXIF:DateTimeOriginal')
        date_time_digitized = d.get('EXIF:CreateDate')
        date_time_sub_sec = d.get('EXIF:SubSecTime', '0')
        date_time_original_sub_sec = d.get('EXIF:SubSecTimeOriginal', '0')
        date_time_digitized_sub_sec = d.get('EXIF:SubSecTimeDigitized', '0')

        gps_latitude = d.get('EXIF:GPSLatitude')
        gps_longitude = d.get('EXIF:GPSLongitude')

        if gps_latitude is not None and d.get('EXIF:GPSLatitudeRef') == 'S':
            gps_latitude = -gps_latitude
        if gps_longitude is not None and d.get('EXIF:GPSLongitudeRef') == 'W':
            gps_longitude = -gps_longitude

        return ExifData(
            d.get('File:MIMEType'),
            d.get('EXIF:Make'),
            d.get('EXIF:Model'),
            parse_exif_date(date_time, date_time_sub_sec),
            parse_exif_date(date_time_original, date_time_original_sub_sec),
            parse_exif_date(date_time_digitized, date_time_digitized_sub_sec),
            None,
            d.get('EXIF:Software'),
            gps_latitude,
            gps_longitude,
            d.get('EXIF:GPSAltitude'),
            d.get('EXIF:ExifImageWidth') or d.get('MakerNotes:CropWidth'),
            d.get('EXIF:ExifImageHeight') or d.get('MakerNotes:CropHeight'),
        )

    @staticmethod
    def _from_video_quicktime(d: dict) -> ExifData:
        date_time = d.get('QuickTime:CreationDate')
        date_time_original = d.get('QuickTime:CreateDate')
        date_time_digitized = d.get('QuickTime:ModifyDate')

        return ExifData(
            d.get('File:MIMEType'),
            d.get('QuickTime:Make'),
            d.get('QuickTime:Model'),
            parse_exif_date(date_time),
            parse_exif_date(date_time_original),
            parse_exif_date(date_time_digitized),
            d.get('QuickTime:Duration'),
            d.get('QuickTime:Software'),
            d.get('Composite:GPSLatitude'),
            d.get('Composite:GPSLongitude'),
            d.get('Composite:GPSAltitude'),
            d.get('QuickTime:ImageWidth'),
            d.get('QuickTime:ImageHeight'),
        )

    @staticmethod
    def _from_video_m2ts(d: dict) -> ExifData:
        date_time = d.get('H264:DateTimeOriginal')

        return ExifData(
            d.get('File:MIMEType'),
            d.get('H264:Make'),
            d.get('H264:Model'),                # Not confirmed
            parse_exif_date(date_time[:19]),
            None,
            None,
            d.get('M2TS:Duration'),
            d.get('M2TS:Software'),             # Not confirmed
            d.get('Composite:GPSLatitude'),     # Not confirmed
            d.get('Composite:GPSLongitude'),    # Not confirmed
            d.get('Composite:GPSAltitude'),     # Not confirmed
            d.get('H264:ImageWidth'),
            d.get('H264:ImageHeight'),
        )

    @staticmethod
    def _from_video_mp4(d: dict) -> ExifData:
        date_time = d.get('QuickTime:CreationDate')
        date_time_original = d.get('QuickTime:CreateDate')
        date_time_digitized = d.get('QuickTime:ModifyDate')

        return ExifData(
            d.get('File:MIMEType'),
            d.get('QuickTime:Make'),
            d.get('QuickTime:Model'),
            parse_exif_date(date_time),
            parse_exif_date(date_time_original),
            parse_exif_date(date_time_digitized),
            d.get('QuickTime:Duration'),
            d.get('QuickTime:Software'),    # Not confirmed
            d.get('Composite:GPSLatitude'),
            d.get('Composite:GPSLongitude'),
            d.get('Composite:GPSAltitude'),
            d.get('QuickTime:ImageWidth'),
            d.get('QuickTime:ImageHeight'),
        )

    @staticmethod
    def _from_video_mpg(d: dict) -> ExifData:
        date_time = d.get('MPEG:CreationDate')          # Not confirmed
        date_time_original = d.get('MPEG:CreateDate')   # Not confirmed
        date_time_digitized = d.get('MPEG:ModifyDate')  # Not confirmed

        return ExifData(
            d.get('File:MIMEType'),
            d.get('MPEG:Make'),     # Not confirmed
            d.get('MPEG:Model'),    # Not confirmed
            parse_exif_date(date_time),             # Not confirmed
            parse_exif_date(date_time_original),    # Not confirmed
            parse_exif_date(date_time_digitized),   # Not confirmed
            d.get('MPEG:Duration'),         # Not confirmed
            d.get('MPEG:Duration'),         # Not confirmed
            d.get('Composite:GPSLatitude'),     # Not confirmed
            d.get('Composite:GPSLongitude'),    # Not confirmed
            d.get('Composite:GPSAltitude'),     # Not confirmed
            d.get('MPEG:ImageWidth'),
            d.get('MPEG:ImageHeight'),
        )

    @staticmethod
    def _from_video_avi(d: dict) -> ExifData:
        date_time = d.get('RIFF:DateTimeOriginal')
        date_time_original = d.get('RIFF:CreateDate')      # Not confirmed
        date_time_digitized = d.get('RIFF:ModifyDate')     # Not confirmed

        return ExifData(
            d.get('File:MIMEType'),
            d.get('RIFF:Make'),    # Not confirmed
            d.get('RIFF:Model'),   # Not confirmed
            parse_exif_date(date_time),             # Not confirmed
            parse_exif_date(date_time_original),    # Not confirmed
            parse_exif_date(date_time_digitized),   # Not confirmed
            d.get('RIFF:Duration'),
            d.get('RIFF:Software'),
            d.get('Composite:GPSLatitude'),     # Not confirmed
            d.get('Composite:GPSLongitude'),    # Not confirmed
            d.get('Composite:GPSAltitude'),     # Not confirmed
            d.get('RIFF:ImageWidth'),
            d.get('RIFF:ImageHeight'),
        )
