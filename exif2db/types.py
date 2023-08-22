import time
from enum import Enum, auto
from typing import Optional
from abc import ABC
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path


class Method(Enum):
    NotSet = auto()
    Combined = auto()
    Exif = auto()
    Pillow = auto()
    Exiftool = auto()


@dataclass
class FileInfo:
    file_date_created: Optional[datetime]
    file_date_modified: Optional[datetime]
    size: Optional[int]
    hash: Optional[str]


@dataclass
class ExifData:
    mime_type: Optional[str]
    make: Optional[str]
    model: Optional[str]
    date_time: Optional[datetime]
    date_time_original: Optional[datetime]
    date_time_digitized: Optional[datetime]
    duration: Optional[float]
    software: Optional[str]
    gps_lat: Optional[float]
    gps_long: Optional[float]
    gps_alt: Optional[float]
    width: Optional[int]
    height: Optional[int]


DEFAULT_FILE_INFO = FileInfo(*(None,) * len(fields(FileInfo)))
DEFAULT_EXIF_DATA = ExifData(*(None,) * len(fields(ExifData)))


class CommitStrategy(ABC):
    def __init__(self):
        self.reset()

    def attempt(self) -> bool:
        ...

    def reset(self):
        ...


class TimeLimit(CommitStrategy):
    def __init__(self, limit_s: float):
        self.limit_s = limit_s
        self.previous = 0
        super().__init__()

    def reset(self):
        self.previous = time.monotonic()

    def attempt(self) -> bool:
        now = time.monotonic()
        if now - self.previous > self.limit_s:
            self.previous = now
            return True
        else:
            return False


class CountLimit(CommitStrategy):
    def __init__(self, max_count: int):
        self.max_count = max_count
        self.current_count = 0
        super().__init__()

    def reset(self):
        self.current_count = 0

    def attempt(self) -> bool:
        if self.current_count > self.max_count:
            self.current_count = 0
            return True
        else:
            return False


class TimeOrCountLimit(CommitStrategy):
    def __int__(self, limit_s: float, max_count: int):
        self.time_limit_strategy = TimeLimit(limit_s)
        self.count_limit_strategy = CountLimit(max_count)
        super().__init__()

    def reset(self):
        self.time_limit_strategy.reset()
        self.count_limit_strategy.reset()

    def attempt(self) -> bool:
        if self.time_limit_strategy.attempt() or self.count_limit_strategy.attempt():
            self.time_limit_strategy.reset()
            self.count_limit_strategy.reset()
            return True
        else:
            return False


class Db(ABC):
    def add_file(self, path: Path):
        ...

    def add_metadata(self, file_id: int, fi: FileInfo, exif: ExifData, method: str):
        ...

    def reset_files_data(self):
        ...

    def reset_exif_data(self):
        ...

    def commit(self):
        pass

    def close(self):
        pass

    def get_all_files(self, prefix: str):
        ...

    def get_files_count(self, prefix: str):
        ...


class ExifReader(ABC):
    _method: Method = Method.NotSet

    def __init__(self, path: Path):
        self.path = path

    def load(self):
        ...

    @property
    def method(self):
        return self._method


class ExifError(Exception):
    pass


class MethodNotFoundError(Exception):
    pass
