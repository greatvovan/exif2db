with src as (
  -- Source with canonized path.
  select substr(path, 31) as path, m.*
  from files f
  join metadata m on f.id = m.id
  where path like '/volumeUSB1/usbshare1-1/Photo/%'
),
dst as (
  -- Destination with canonized path.
  select substr(path, 16) as path, m.*
  from files f
  join metadata m on f.id = m.id
  where path like '/volume1/Photo/%'
),
src_only_path as (
  -- Path is present only in the source.
  select 'Src only path' as status, src.*
  from src
  where path not in (select path from dst)
),
dst_only_path as (
  -- Path is present only in the destination.
  select 'Dst only path' as status, dst.*
  from dst
  where path not in (select path from src)
),
src_only_hash as (
  -- The file is present only in the source (regardless of path).
  select 'Src only hash' as status, src.*
  from src
  where hash not in (select hash from dst)
),
dst_only_hash as (
  -- The file is present only in the destination (regardless of path).
  select 'Dst only hash' as status, dst.*
  from dst
  where hash not in (select hash from src)
),
changed as (
  -- Path matches but the content is different.
  select 'Changed' as status, src.*
  from src
  join dst on src.path = dst.path
  where src.hash != dst.hash
),
summary as (
  select * from src_only_path
  union all
  select * from dst_only_path
  union all
  select * from src_only_hash
  union all
  select * from dst_only_hash
  union all
  select * from changed
)
select *
from summary
-- order by status, path