#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author Alexander Heinz, alexander.heinz@saturn.uni-freiburg.de
@license BSD
"""

import os

quality = [
            ('Pretty', '/home/alex/configs/mpv/mpv_quality.conf'),
            ('Fast', '/home/alex/configs/mpv/mpv_fast.conf')
          ]
conf = '/home/alex/.config/mpv/mpv.conf'


def notify(msg):
    os.system('notify-send -t 5000 -a \"MPV Conf\" \"MPV Conf\" \"' +
              msg + '\"')


def getToggleConf():
    rp = os.path.realpath(conf)
    c_len = len(quality)
    n_conf = ""

    for i in range(0, c_len):
        if quality[i][1] == rp:
            if i < c_len - 1:
                n_conf = quality[i+1]
            else:
                n_conf = quality[0]

    if not n_conf:
        n_conf = quality[0]

    return n_conf

if __name__ == "__main__":
    n_conf = getToggleConf()
    os.system('rm ' + conf + ' && ln -s ' + n_conf[1] + ' ' + conf)
    notify('Set to mode ' + n_conf[0])
    exit(0)
