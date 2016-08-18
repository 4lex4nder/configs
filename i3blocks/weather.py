#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author Alexander Heinz, alexander.heinz@saturn.uni-freiburg.de
@license BSD
"""

import json
import os
import re
import urllib.request
from html.parser import HTMLParser

pango_mode = True

color00="#272822"
color01="#f92672"
color02="#a6e22e"
color03="#f4bf75"
color04="#66d9ef"
color05="#ae81ff"
color06="#a1efe4"
color07="#f8f8f2"
color_foreground="#383830"
color_background="#fd971f"
color_separator="#383830"

icon_map = {'heiter': ['', ''],
            'bewölkt': ['', ''],
            'leicht bewölkt': ['', ''],
            'stark bewölkt': ['', ''],
            'leichter Regen': ['', ''],
            'Regen': ['', ''],
            'Regenschauer': ['', '']
            }


locations = ['Freiburg_im_Breisgau', 'Loerrach']
url = 'http://www.wetterdienst.de/Deutschlandwetter/{location}/'
cache = '/tmp/weather.cache'
d_order = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa']
t_order = ['Morgens', 'Mittags', 'Abends', 'Nachts']


def get_day(data):
    return data[1].split()[0].strip()


def get_day_dist(org, dest):
    i_o = d_order.index(org) + 1
    d_o = d_order.index(dest) + 1

    if d_o < i_o:
        return d_o + len(d_order) - i_o
    elif d_o > i_o:
        return d_o - i_o
    else:
        return 0


def get_time(data):
    return data[2][0]


def _comperator(x, y):
    day1 = get_day(x)
    day2 = get_day(y)
    # time1 = get_time(x)
    # time2 = get_time(y)

    org = x[0]
    dist_1 = get_day_dist(org, day1)
    dist_2 = get_day_dist(org, day2)

    dist = dist_1 - dist_2

    # if dist == 0:
    #    i_t1 = t_order.index(time1) + 1
    #    i_t2 = t_order.index(time2) + 1

    #    return i_t2 - i_t1
    # else:
    return dist


def cmp_to_key(mycmp):
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K


class MyHTMLParser(HTMLParser):
    weather_data = []
    weather_recent = ''

    date_start = False
    current_date = ''

    forecast_start = False
    time_start = False
    current_time = []

    content_start = False
    ending_start = False

    weather_start = False
    weather = []

    temp_start = False
    temp = []

    rot_start = False
    rot = ''

    def get_sorted_weather_data(self):
        return sorted(self.weather_data, key=cmp_to_key(_comperator))

    def _sort_data(self):
        time = self.weather[0]
        celest = self.weather[1]
        tday = self.current_time
        p_rain = ''
        feel = list(filter(lambda x: re.match('[0-9]+', x), self.rot.split()))
        real = list(filter(lambda x: re.match('[0-9]+', x), self.temp))

        for i in range(0, len(self.weather)):
            el = self.weather[i]
            if el == 'Niederschlag:':
                nEl = self.weather[i+1]
                if nEl == '<':
                    p_rain = '&lt;' + self.weather[i+2]
                elif nEl == '>':
                    p_rain = '&gt;' + self.weather[i+2]
                else:
                    p_rain = nEl

        if not self.weather_recent:
            self.weather_recent = time.split()[0].strip()

        wdata = (self.weather_recent, time, tday, celest, real, feel, p_rain)
        # print(get_day(wdata))
        # print(tday)
        self.weather_data.append(wdata)

        self.temp = []
        self.weather = []
        self.current_time = []

    def handle_starttag(self, tag, attrs):
        if tag == 'h2' and ('class', 'date') in attrs:
            self.date_start = True
        if tag == 'div' and ('class', 'forecast_box') in attrs:
            self.forecast_start = True
        if tag == 'div' and ('class', 'forecast_content') in attrs \
                and self.forecast_start:
            self.content_start = True
        if tag == 'div' and ('class', 'forecast_weather') in attrs \
                and self.content_start:
            self.weather_start = True
        if tag == 'div' and ('class', 'forecast_temp') in attrs \
                and self.content_start:
            self.temp_start = True
        if tag == 'div' and ('class', 'forecast_rot') in attrs \
                and self.content_start:
            self.rot_start = True
        if tag == 'div' and ('class', 'forecast_details_link') in attrs \
                and self.content_start:
            self.ending_start = True
        if tag == 'h3' and self.forecast_start:
            self.time_start = True

    def handle_endtag(self, tag):
        if tag == 'h2' and self.date_start:
            self.date_start = False
        if tag == 'h3' and self.time_start:
            self.time_start = False
        if tag == 'div' and self.weather_start:
            self.weather_start = False
        if tag == 'div' and self.temp_start:
            self.temp_start = False
        if tag == 'div' and self.rot_start:
            self.rot_start = False
        if tag == 'div' and self.ending_start:
            self.ending_start = False
            self.content_start = False
            self.forecast_start = False
            self._sort_data()

    def handle_data(self, data):
        if self.date_start:
            self.current_date = data
        if self.time_start:
            sdate = data.strip()
            if sdate:
                self.current_time.append(data.strip())
        if self.weather_start:
            sweather = data.strip()
            if sweather:
                self.weather.append(sweather)
        if self.temp_start:
            stemp = data.strip()
            if stemp:
                self.temp.append(stemp)
        if self.rot_start:
            self.rot = data.strip()


def notify(msg):
    os.system('notify-send -t 5000 -a \"Weather\" \"Weather\" \"' + msg + '\"')


def readCache():
    try:
        with open(cache, 'r+') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def writeCache(data):
    with open(cache, 'w+') as f:
        json.dump(data, f)


def getCurrentWeather():
    w = readCache()
    p = w[1][locations[w[0][1]]]
    return p[w[0][0]]


def updateWeather():
    weather = {}

    for loc in locations:
        lurl = url.format(location=loc)
        req = urllib.request.urlopen(lurl)
        content = str(req.read().decode('utf-8'))
        req.close()
        parser = MyHTMLParser()
        parser.feed(content)
        weather[loc] = parser.get_sorted_weather_data()

    oldweather = readCache()

    if oldweather:
        writeCache((oldweather[0], weather))
    else:
        writeCache(((0, 0),  weather))


def iterateLocation():
    w = readCache()
    if not w:
        return

    l = w[0][1]
    l += 1

    if l > len(locations) - 1:
        l = 0

    w[0][1] = l

    writeCache(w)
    notify('Location set to ' + locations[l])


def scrollUp():
    w = readCache()
    if not w:
        return

    wl = w[1][locations[w[0][1]]]
    l = w[0][0]
    l += 1

    if l > len(wl) - 1:
        l -= 1

    w[0][0] = l
    writeCache(w)
    notify('Time set to: ' + wl[l][1])


def scrollDown():
    w = readCache()
    if not w:
        return

    wl = w[1][locations[w[0][1]]]
    l = w[0][0]
    l -= 1

    if l < 0:
        l = 0

    w[0][0] = l
    writeCache(w)
    notify('Time set to: ' + wl[l][1])


def get_statusmessage():
    weather = getCurrentWeather()
    icon = icon_map[weather[3]]
    temp = weather[4]
    prain = weather[6]

    if weather[2][0] == 'Morgens' or weather[2][0] == 'Mittags':
        icon = icon[0]
    else:
        icon = icon[1]

    if len(temp) == 1:
        temp = temp[0] + '°C'
    elif len(temp) == 2:
        temp = temp[0] + '/' + temp[1] + '°C'

    full_text = icon + ' ' + temp

    if prain:
        full_text += ' ' + prain
    color = ''

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
        if ev == '2':
            pass
        elif ev == '3':
            iterateLocation()
        elif ev == '4':
            scrollUp()
        elif ev == '5':
            scrollDown()
        else:
            updateWeather()
    else:
        updateWeather()
    print(get_statusmessage())
    exit(0)
