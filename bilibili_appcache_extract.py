#!/usr/bin/env python
# 从B站的手机APP离线缓存目录中提取视频合并为.mp4文件，
# 并在文件名中标注AV号及UP主昵称。
# Extract videos from offline cache directories
# of bilibili mobile client app, with names including
# the videos' av IDs and the uploaders' names.

import json
import os
import shutil
import sys
from glob import glob
from json import JSONDecodeError

import bs4
import requests

# DEPRECATED:
# from bilibili_video_api import bilibili
# Depends on package `bilibili_video_api` which is derived (2to3) from:
# https://github.com/Vespa314/bilibili-api/tree/master/bilibili-video

ILLEGAL_CHARS = ['\\', '/', ':', '*', '"', '<', '>', '|', '?']


def validate_path(s: str):
    """Only for Windows systems currently, change it as you wish."""
    sp = s
    for i in ILLEGAL_CHARS:
        sp = sp.replace(i, ' ')
    return sp


def ffmpeg_concat(input_list: list, ouput_path: str):
    work_dir, _ = os.path.split(os.path.realpath(ouput_path))
    list_path = os.path.join(work_dir, '###-ffmpeg-concat-list-temp.txt')
    with open(list_path, 'w+b') as lf:
        for i in input_list:
            lf.write("file '{}'{}".format(i, os.linesep).encode())
    os.system(
        'ffmpeg -n -hide_banner -loglevel +level -f concat -safe 0 -i "{}" -c copy "{}"'
            .format(list_path, ouput_path))
    os.remove(list_path)


# def get_author_api(id):
#     appkey = '1d8b6e7d45233436'
#     # 1d8b6e7d45233436
#     # f3bb208b3d081dc8
#     # 85eb6835b0a1034e
#     # 4fa4601d1caa8b48
#     # 452d3958f048c02a
#     # 86385cdc024c0f6c
#     # 5256c25b71989747
#     # e97210393ad42219
#     v = bilibili.GetVideoInfo(id, appkey)
#     return v.author.name.decode()


def get_info_kanbilibili(id):
    url = 'http://www.kanbilibili.com/video/av{}'.format(id)
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.content, 'lxml')
    scripts = soup('script')
    info = scripts[3].text.strip().strip('window.__init__ = ')
    return json.loads(info)


def get_author_kanbilibili(id):
    try:
        return get_info_kanbilibili(id)['author']
    except JSONDecodeError:
        return 'ERR_KANBILI'


class VideoFolder:
    def __init__(self, cached_folder):
        self.folder = cached_folder
        self.work_dir, self.id = os.path.split(os.path.realpath(cached_folder))
        self.part_list = os.listdir(cached_folder)
        self.part_sum = len(self.part_list)
        self.part = None
        self.entry = None

    def handle_part(self):
        print('====== {}'.format(self.folder))
        for part in self.part_list:
            self.part = part
            print('------ {}'.format(part))
            try:
                self.entry = entry = json.load(open(os.path.join(self.folder, part, 'entry.json'), encoding='utf8'))
            except FileNotFoundError:
                os.remove(os.path.join(folder, part))
                continue
            if 'page_data' in entry:
                self.handle_vupload()
            elif 'ep' in entry:
                self.handle_bangumi()

    def handle_vupload(self):
        title = validate_path(self.entry['title'])
        blv_list = glob(os.path.join(self.folder, self.part, self.entry['type_tag'], '*.blv'))
        author = get_author_kanbilibili(self.id)
        output = os.path.join(self.work_dir, '{} [av{}][{}]'.format(title, self.id, author))
        if len(self.part_list) >= 2:
            part_title = validate_path(self.entry['page_data']['part'])
            output += '{}-{}.mp4'.format(self.part, part_title)
        else:
            output += '.mp4'
        ffmpeg_concat(blv_list, output)

    def handle_bangumi(self):
        title = validate_path(self.entry['title'])
        blv_list = glob(os.path.join(self.folder, self.part, self.entry['type_tag'], '*.blv'))
        part_title = validate_path(self.entry['ep']['index_title'])
        av_id = self.entry['ep']['av_id']
        ep_num = self.entry['ep']['index']
        output_dir = os.path.join(self.work_dir, '{} [av{}][{}]'.format(title, av_id, self.id))
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        output = os.path.join(output_dir, '{}. {}.mp4'.format(str(ep_num).zfill(len(str(self.part_sum))), part_title))
        ffmpeg_concat(blv_list, output)
        shutil.copy2(os.path.join(self.folder, self.part, 'danmaku.xml'), output[:-3] + 'xml')


if __name__ == '__main__':
    # _, base = os.path.split(sys.argv[1])
    if sys.argv[1][-1] == '*':
        args = glob(sys.argv[1])
    else:
        args = sys.argv[1:]
    for folder in args:
        if not os.path.isdir(folder):
            continue
        vf = VideoFolder(folder)
        vf.handle_part()
