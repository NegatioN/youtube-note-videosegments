import sqlite3
import snappy
import json
from urllib.parse import urlparse, parse_qs

ext_uuid = '8bf5521e-d809-46aa-8565-5fb1092aed03'
con = sqlite3.connect(f'/home/joakim/.mozilla/firefox/ycbl2bwi.default-release/storage/default/moz-extension+++{ext_uuid}^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite')
cur = con.cursor()

for i, row in enumerate(cur.execute('SELECT * FROM object_data;')):
    name = bytes([b-1 for b in row[1][1:]])
    print(name, snappy.decompress(row[4]))
    print(row[1], row[4])

def to_seconds(time_string):
    mins, secs = time_string.strip().split(':')

    return (int(mins) * 60) + int(secs)

def construct_timestamps(s):
    prefix = b'\x03\x00\x00\x00\x00\x00\xf1\xffL\x00\x00\x80\x04\x00\xff\xff'
    postfix = b'\x00\x00\x00\x00'
    stride = 3
    entries = s.split('::')
    # timestamps in selections need to be inverted to skip the other parts of the video
    timestamps = [0.]
    types = ['c']
    for i in range(0, len(entries), stride):
        start, end = entries[i].split('-')
        timestamps.append(to_seconds(start))
        timestamps.append(to_seconds(end))
        types.append('cs')
        types.append('c')
    types.append()
    types.append('-')
    data = {'timestamps': timestamps, 'types': types}
    return snappy.compress(prefix +json.dumps(data, separators=(',', ':')).encode('utf-8') + postfix)


def parse_document(path):
    '''
        Document format:
        Line 1: a youtube URL
        Other lines: [TimeStart-TimeEnd] :: "Some notes"
        Example: 10:33-44:55 :: "This was cool"
    '''
    with open(path, 'r') as f:
        url = f.readline().strip()
        url_id = parse_qs(urlparse(url).query)['v'][0]
        video_id = bytes([48] + [b+1 for b in bytes(f'youtube-{url_id}', 'utf-8')])
        content = f.read()

        timestamps = construct_timestamps(content)
    return video_id, timestamps

#TODO figure out what \xffL part difference is because of. Some sort of padding probably.
#\x03\x00\x00\x00\x00\x00\xf1\xff9\x00\x00\x80\x04\x00\xff\xff
#\x00\x00\x00\x00\x00\x00\x00

#\x03\x00\x00\x00\x00\x00\xf1\xffa\x00\x00\x80\x04\x00\xff\xff
#\x00\x00\x00\x00\x00\x00\x00
video_id, timestamps = parse_document('/home/joakim/Desktop/maps_of_meaning.txt')


#cur.execute("drop trigger IF EXISTS object_data_insert_trigger")
#cur.execute("insert into object_data(object_store_id, key, data) values (?, ?, ?)", (1, video_id, timestamps))
con.commit()
cur.close()



#drop trigger object_data_insert_trigger; must be in place to insert stuff.
