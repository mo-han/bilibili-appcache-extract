#!/usr/bin/env python
# 从B站的手机APP离线缓存目录中提取视频合并为.mp4文件，
# 并在文件名中标注AV号及UP主昵称。
# Extract videos from offline cache directories
# of bilibili mobile client app, with names including
# the videos' av IDs and the uploaders' names.

import json
import os
import sys
from glob import glob
from time import sleep

import bs4
import lxml
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
    return get_info_kanbilibili(id)['author']


_, base = os.path.split(sys.argv[1])
if base == '*':
    args = glob(sys.argv[1])
else:
    args = sys.argv[1:]
for d in args:
    if not os.path.isdir(d):
        continue
    print(d)
    work_dir, id = os.path.split(os.path.realpath(d))
    author = get_author_kanbilibili(id)
    p_l = os.listdir(d)
    for p in p_l:
        e = json.load(open(os.path.join(d, p, 'entry.json'), encoding='utf8'))
        blv_list = glob(os.path.join(d, p, e['type_tag'], '*.blv'))
        il = []
        for i in blv_list:
            il += [i]
        title = e['title']
        title = validate_path(title)
        o = os.path.join(work_dir, '{} [av{}][{}]'.format(title, id, author))
        if len(p_l) >= 2:
            ptitle = e['page_data']['part']
            ptitle = validate_path(ptitle)
            o += '{}-{}.mp4'.format(p, ptitle)
        else:
            o += '.mp4'
        ffmpeg_concat(il, o)
