## exif2db

Scan your photo library and store photo metadata into an Sqlite database.

Gain full control over file indexing and search! Abandon the photo management
tools that do only one half and cannot do another half of work that you need.

The module scans your photo collection and populates an SQLite database with
the most essential information, so that later you can use power of SQL and
relational database to perform any kind of search and analysis.

`python -m exif2db -d photos.db --with_hash --exclude @eaDir --exclude [Originals] --purge /volume1/Photo`

## Syntax

`exif2db [-h] [-e EXT] [-d DATABASE] [--purge] [--with_hash] [--no_scan] [-x PATTERN] path`

```text
  path                  Path to the media library. Content will be scanned recursively.

options:
  -h, --help            show help message
  -e EXT, --ext EXT     Filter on these file name extensions, comma-separated list.
  -d DATABASE, --database DATABASE
                        Location of SQLite database. Defaults to ./sqlite.db
  --purge               Purge the database if not empty.
  --with_hash           Calculate SHA1 hash for each file
  --no_scan             Do not perform new file scan (continue after a failure).
  -x PATTERN, --exclude PATTERN
                        Exclude pattern for files and directories
```

The database consists of two tables: `files` and `metadata`. The first one
contains just paths and is filled on the scan stage. The second one
contains extracted metadata, as well as file properties and hashes (if this
option was enabled).

If the database file already exists, the data will not be erased,
new content will be added instead. If this is not desired, `--purge`
key will truncate tables.

`--no_scan` option is meant for interrupted scans and allows to avoid
population of `files` table.

## Examples
