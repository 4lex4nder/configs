#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author Alexander Heinz, alexander.heinz@saturn.uni-freiburg.de
@license BSD
"""

import json
import os

pango_mode = True
log = True
logfile = '/home/alex/logs/notifications.log'
logapps = ['KDE-Connect']

color00="#272822"
color01="#f92672"
color02="#a6e22e"
color03="#f4bf75"
color04="#66d9ef"
color05="#ae81ff"
color06="#a1efe4"
color07="#f8f8f2"
color_foreground="#383830"
color_background="#f8f8f2"
color_separator="#383830"


def _f_kde_connect(a, b, s):
    ico = ''
    clr = ''

    if b.startswith('WhatsApp'):
        b = b[10:]
        clr = color02
        ico = ''

    msg = ico + ' ' + b

    return (msg, clr)


def _f_spotify(a, b, s):
    ico = ''
    clr = ''
    spl = b.split('-', 1)
    singer = spl[0].strip()
    album = spl[1].strip()
    msg = ico + ' ' + singer + ' - ' + s + ' [' + album + ']'

    return (msg, clr)


def _f_pidgin(a, b, s):
    ico = ''
    clr = ''

    if s.startswith('Buddy signed on'):
        ico = ''
    elif s.startswith('Buddy signed off'):
        ico = ''
    else:
        ico = ''

    name = b

    if '(' in b and ')' in b:
        name = b.split('(', 1)[1]
        name = name[:len(name)-1]

    msg = ico + ' ' + name + ': ' + s

    return (msg, clr)


def _f_irssi(a, b, s):
    ico = ''
    msg = ico + ' ' + b

    return (msg, '')


# available configuration parameters
fmt = '{appname} {summary} {body}'
tmp_path = '/tmp/statnot_cache'
_file_tmp = open(tmp_path, 'r')

fmap = {
        'KDE-Connect': _f_kde_connect,
        'Spotify': _f_spotify,
        'Pidgin': _f_pidgin,
        'Irssi': _f_irssi,
        'Weather': (lambda a, b, s: (' ' + b, ''))
        }

max_chars = 70


def _trunc_message(ftext, queue):
    queue_len = len(queue)
    if len(ftext) + queue_len > max_chars:
        return ftext[:max_chars-3-queue_len] + '...' + queue
    else:
        return ftext + queue


def get_statusmessage():
    # create an output text replacing the placeholder
    n_data = json.load(_file_tmp)
    color = ''
    full_text = ''

    # Format data
    if not n_data:
        full_text = ''
    else:
        if n_data[0] in fmap:
            (full_text, color) = fmap[n_data[0]](n_data[0],
                                                 n_data[3], n_data[2])
        else:
            icon = n_data[0] + ': '
            full_text = fmt.format(appname=icon,
                                   summary=n_data[2], body=n_data[3])

        queue_text = ''
        if n_data[5] > 1:
            queue_text = ' (' + str(n_data[5]) + ')'
        full_text = _trunc_message(full_text, queue_text)

        if log and n_data[0] in logapps:
            with open(logfile, 'a') as f:
                f.write(n_data[0] + ':' + n_data[3] + ':' + n_data[2] + '\n')

    # Return empty, otherwise pango tags might
    # be picked up and seperator drawn.
    if not full_text:
        return ''

    response = ''
    # Format to pango if flag set and make sure to enable font fallback.
    if not pango_mode:
        response = full_text + '\n' + full_text + '\n' + color
    else:
        bg = ''
        if color:
            bg = color
        else:
            bg = color_background

        if color_separator:
            response = '<span background="' + color_separator +\
                       '" foreground="' + bg + '"></span>'

        response += '<span foreground="' + color_foreground +\
                    '"background="' + bg + '">' + full_text + '</span>'

        if color_separator:
            response += '<span background="' + bg +\
                       '" foreground="' + color_separator + '"></span>'

    return response


if __name__ == "__main__":
    ev = ''
    if 'BLOCK_BUTTON' in os.environ:
        ev = os.environ['BLOCK_BUTTON']
        if ev == '1':
            os.system('echo \"[]\" > /tmp/statnot_cache')
    print(get_statusmessage())
    exit(0)
