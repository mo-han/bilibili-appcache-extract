#!/usr/bin/env python
# 从B站的手机APP离线缓存目录中提取视频合并为.mp4文件，
# 并在文件名中标注AV号及UP主昵称。
# Extract videos from offline cache directories
# of bilibili mobile client app, with names including
# the videos' av IDs and the uploaders' names.

import json
import sys
from glob import glob
from os import listdir, path, system
# Depends on package `bilibili_video_api` which is derived (2to3) from:
# https://github.com/Vespa314/bilibili-api/tree/master/bilibili-video
from bilibili_video_api import bilibili

ILLEGAL_CHARS = ['NUL','\\','/',':','*','"','<','>','|']


def safe_path(s: str):
    """Only for Windows systems currently, change it as you wish."""
    sp = s
    for i in ILLEGAL_CHARS:
        sp = sp.replace(i, ' ')
    return sp


def get_video_uploader(id):
    appkey = '1d8b6e7d45233436'
    # appkey = 'f3bb208b3d081dc8'
    # appkey = '85eb6835b0a1034e'
    v = bilibili.GetVideoInfo(id, appkey)
    return v.author.name.decode()


for d in sys.argv[1:]:
    parent_dir, id = path.split(path.realpath(d))
    uploader = safe_path(get_video_uploader(id))
    for p in listdir(d):
        e = json.load(open('{}/{}/entry.json'.format(d, p), encoding='utf8'))
        e['title'] = safe_path(e['title'])
        blv_list = glob('{}/{}/{}/*.blv'.format(d, p, e['type_tag']))
        cmd = 'ffmpeg-concat.bat '
        for i in blv_list:
            cmd += '"{}" '.format(i)
        cmd += '"{}/{} [av{}][{}]"'.format(parent_dir, e['title'], id, uploader)
        if p != '1': 
            cmd += '{}'.format(p)
        cmd += '.mp4'
        system(cmd)
