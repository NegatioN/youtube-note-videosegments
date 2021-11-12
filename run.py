import os
import subprocess
from yt_dlp import YoutubeDL
import argparse

parser = argparse.ArgumentParser(description='Create highlight-clip from notes.')
parser.add_argument('-f', '--filepath', type=str)
parser.add_argument('-t', '--targetpath', type=str)
args = parser.parse_args()
video_filename = os.path.basename(args.filepath).split('.')[0]

def get_download_link(link):
    with YoutubeDL() as y:
        r = y.extract_info(link, download=False)
        formats = r['formats']
        # sort all formats by size, highest is probably the best quality mp4.
        sorted_formats = list(sorted([f for f in formats if f['filesize']], key=lambda x: int(x['filesize']), reverse=False))
        best_audio = [x for x in sorted_formats if x['acodec'] != 'none' and x['fps'] == None][-1]
        best_video = sorted_formats[-1]

        print('Using video:', best_video['format_note'])
        print('Using audio:', best_audio['format_note'])
        return best_video['url'], best_audio['url']


def to_seconds(time_string):
    mins, secs = time_string.strip().split(':')
    return (int(mins) * 60) + int(secs)

def construct_timestamps(s):
    stride = 2
    entries = s.split('::')
    timestamps = []
    for i in range(1, len(entries), stride):
        start, end = entries[i].split('-')
        timestamps.append((to_seconds(start), to_seconds(end)))

    return timestamps

def parse_document(path):
    '''
        Document format:
        Line 1: a youtube URL
        Other lines: :: [TimeStart-TimeEnd] :: "Some notes"
        Example: :: 10:33-44:55 :: "This was cool"
    '''
    with open(path, 'r') as f:
        url = f.readline().strip()
        content = f.read()
        timestamps = construct_timestamps(content)
    return url, timestamps

video_url, timestamps = parse_document(args.filepath)

vid_url, audio_url = get_download_link(video_url)

COMMAND = 'ffmpeg '
channels = ''
for i, (start, end) in enumerate(timestamps):
    COMMAND += f'-ss {start} -to {end} -i "{vid_url}" -ss {start} -to {end} -i "{audio_url}" ' # Doing this allows us to only download the relevant parts of the video
    channels += f'[{i * 2}:v][{(i * 2) + 1}:a]'

COMMAND += f'-filter_complex "{channels}concat=n={i + 1}:v=1:a=1[v][a]" -map "[v]" -map "[a]" {os.path.join(args.targetpath, video_filename)}.mp4'

proc = subprocess.run(COMMAND, shell=True, capture_output=True)
print(proc.stdout)
print(proc.stderr)