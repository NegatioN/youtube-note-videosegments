import sqlite3
import snappy
import json
ext_uuid = '8bf5521e-d809-46aa-8565-5fb1092aed03'
con = sqlite3.connect(f'/home/joakim/.mozilla/firefox/ycbl2bwi.default-release/storage/default/moz-extension+++{ext_uuid}^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite')
cur = con.cursor()

for i, row in enumerate(cur.execute('SELECT * FROM object_data;')):
    name = bytes([b-1 for b in row[1][1:]])
    print(name, snappy.decompress(row[4]))
video_id = bytes([48] + [b+1 for b in b'youtube-2QmFxwOzO_o'])
print(video_id)

data = {'timestamps': [1.5],
        'types': ['c', '-']}

#TODO figure out what \xffL part difference is because of. Some sort of padding probably.
#\x03\x00\x00\x00\x00\x00\xf1\xff9\x00\x00\x80\x04\x00\xff\xff
#\x00\x00\x00\x00\x00\x00\x00

#\x03\x00\x00\x00\x00\x00\xf1\xffa\x00\x00\x80\x04\x00\xff\xff
#\x00\x00\x00\x00\x00\x00\x00
prefix = b'\x04\x03\x00\x01\x01\xd8\xf1\xffL\x00\x00\x80\x04\x00\xff\xff'
postfix = b'\x00\x00\x00\x00'
s = snappy.compress(prefix +json.dumps(data).encode('utf-8') + postfix)
print(s)
#cur.execute("insert into object_data(object_store_id, key, data) values (?, ?, ?)", (1, video_id, s))
con.commit()
cur.close()

#drop trigger object_data_insert_trigger; must be in place to insert stuff.
