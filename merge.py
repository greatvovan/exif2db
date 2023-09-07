from argparse import ArgumentParser
from tqdm import tqdm
from exif2db.sqlite import Sqlite


parser = ArgumentParser('merge', 'Merge two exif2db DBs into one')
parser.add_argument('source', help='Source')
parser.add_argument('destination', help='Destination')
args = parser.parse_args()

src = Sqlite(args.source)
dst = Sqlite(args.destination)

for fm in tqdm(src.get_all_raw()):
    dst.file_num += 1
    path, status = fm[1:3]
    dst.add_file_raw(dst.file_num, path, status)
    if fm[3] is not None:
        dst.add_metadata_raw((dst.file_num,) + fm[4:])

dst.commit()
