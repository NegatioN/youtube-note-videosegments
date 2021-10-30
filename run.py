import subprocess
from youtube_dl import YoutubeDL
import json
from urllib.parse import urlparse, parse_qs

def get_download_link(link):
    with YoutubeDL() as y:
        r = y.extract_info(link, download=False)
        return r['formats'][-1]['url']


def to_seconds(time_string):
    mins, secs = time_string.strip().split(':')
    return (int(mins) * 60) + int(secs)

def construct_timestamps(s):
    stride = 3
    entries = s.split('::')
    timestamps = []
    print(entries)
    for i in range(0, len(entries), stride):
        start, end = entries[i].split('-')
        timestamps.append((to_seconds(start), to_seconds(end)))

    return timestamps

def parse_document(path):
    '''
        Document format:
        Line 1: a youtube URL
        Other lines: [TimeStart-TimeEnd] :: "Some notes"
        Example: 10:33-44:55 :: "This was cool"
    '''
    with open(path, 'r') as f:
        url = f.readline().strip()
        content = f.read()
        timestamps = construct_timestamps(content)
    return url, timestamps

video_url, timestamps = parse_document('/home/joakim/Desktop/maps_of_meaning.txt')

print(video_url)
print(timestamps)

true_url = get_download_link(video_url)

fade = 0.05
# Build ffmpeg command

#target_file = 'video.mp4'
target_file = true_url

COMMAND = 'ffmpeg '
for start, end in timestamps:
    COMMAND += f'-ss {start} -to {end} -i "{target_file}" ' # Not fast-seeking seems incredibly slow, so thats why we do this

complex_filter = '[0:v]setpts=PTS-STARTPTS[0v];[0:a]asetpts=PTS-STARTPTS[0a];'
voffset = (timestamps[0][1] - timestamps[0][0]) - fade

for i, (start, end) in enumerate(timestamps[1:], 1):
    complex_filter += f'[{i}:v]setpts=PTS-STARTPTS[{i}v];[{i}:a]asetpts=PTS-STARTPTS[{i}a];'
    complex_filter += f'[{i-1}v][{i}v]xfade=offset={voffset:.3f}:duration={fade:.3f}[{i}v];[{i-1}a][{i}a]acrossfade=duration={fade}[{i}a];'
    voffset += (end - start) - fade

    COMMAND = f"{COMMAND} -filter_complex '{complex_filter[:-1]}' -map '[{i}v]' -map '[{i}a]' output.mp4"

#PLAN: https://unix.stackexchange.com/questions/230481/how-to-download-portion-of-video-with-youtube-dl-command

#output = subprocess.run(COMMAND, shell=True, capture_output=True)
print(COMMAND)