#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author Alexander Heinz, alexander.heinz@saturn.uni-freiburg.de
@license BSD
"""
import os
import matplotlib.colors as cl
import math


def stripChar(string, char):
    return ''.join(map(lambda x: x if x != char else '', string))


i3_conf = '/home/alex/.i3/config'
i3_blocks = [
                ('/home/alex/.config/i3blocks/shutdown', 'sh', 'color01'),
                ('/home/alex/.config/i3blocks/date', 'sh', 'color07'),
                ('/home/alex/.config/i3blocks/weather.py', 'py', 'color16'),
                ('/home/alex/.config/i3blocks/battery', 'pl', 'color02'),
                ('/home/alex/.config/i3blocks/cpu_usage', 'pl', 'color03'),
                ('/home/alex/.config/i3blocks/wifi', 'sh', 'color04'),
                ('/home/alex/.config/i3blocks/disk', 'sh', 'color05'),
                ('/home/alex/.config/i3blocks/volume', 'sh', 'color06'),
                ('/home/alex/.config/i3blocks/statnot_tmp.py', 'py', 'color07')
                # ('/home/alex/.config/i3blocks/statnot_tmp.py', 'py')
            ]
st_config = '/home/alex/Documents/sway/st/config.h'
rofi_t = '/usr/bin/rofit'


def get_color_by_num(colors, num):
    c_str = 'color' + str(num) if num > 9 else 'color0' + str(num)
    return colors[c_str]


# (org, des, step): (CLR, CLR, FLOAT)
def get_gradient(org, des, step):
    c_org = cl.hex2color(org)
    c_des = cl.hex2color(des)
    c_gra = (c_org[0] + step * (c_des[0] - c_org[0]),
             c_org[1] + step * (c_des[1] - c_org[1]),
             c_org[2] + step * (c_des[2] - c_org[2]))
    return cl.rgb2hex(c_gra)


def clip_value(val):
    if val < 0.0:
        return 0.0
    if val > 1.0:
        return 1.0

    return val


def get_colors_mult(clr, step):
    c_clr = cl.hex2color(clr)
    c_r = clip_value(c_clr[0] * step)
    c_g = clip_value(c_clr[1] * step)
    c_b = clip_value(c_clr[2] * step)

    return cl.rgb2hex((c_r, c_g, c_b))


# Returns the normalized distance (non-euclidian!) to predefined color
def get_distance(org, des):
    c_org = cl.hex2color(org)
    c_des = cl.hex2color(des)

    # To power of two to punish greater deviations more.
    dist_rgb = (math.pow(c_des[0] - c_org[0], 2.0),
                math.pow(c_des[1] - c_org[1], 2.0),
                math.pow(c_des[2] - c_org[2], 2.0))

    return (dist_rgb[0] + dist_rgb[1] + dist_rgb[2]) / float(3)


def match_var(colors, line, decl, vprefix, prefix, eq, suffix):
    if line.startswith(decl):
        setter = line.split()

        if len(setter) < 2:
            setter = line.split(eq)
            if len(setter) < 2:
                return line

        var = ''
        if decl:
            var = setter[1][len(vprefix):].strip()
        else:
            var = setter[0].strip()

        if var in colors:
            if decl:
                return str(decl + ' ' + vprefix + var + eq +
                           prefix + colors[var] + suffix + '\n')
            else:
                return str(vprefix + var + eq +
                           prefix + colors[var] + suffix + '\n')

        else:
            return line
    else:
        return line


def set_colors(colors, f_in, typ):
    out = []
    with open(f_in) as f:
        for line in f:
            if typ == 'sh' or typ == 'py':
                out.append(match_var(colors, line, '', '', '\"', '=', '\"'))
            elif typ == 'pl':
                out.append(match_var(colors, line, 'my', '$', '\"', ' = ',
                                     '\";'))
            elif typ == 'i3':
                out.append(match_var(colors, line, 'set', '$', '\t\t', '', ''))
    outp = open(f_in, 'w+')
    outp.writelines(out)
    outp.flush()
    outp.close()


def set_st_colors_fill(arr, colors):
    for i in range(0, 16):
        arr.append('    \"' + get_color_by_num(colors, i).upper() + '\",\n')
    arr.append('\n    [255] = 0,\n\n')
    arr.append('    \"' + get_color_by_num(colors, 20).upper() + '\",\n')
    arr.append('    \"' + get_color_by_num(colors, 19).upper() + '\",\n')


def set_st_colors(colors, header):
    started = False
    out = []
    with open(header) as f:
        for line in f:
            if started and not line.startswith('};'):
                continue
            elif started and line.startswith('};'):
                set_st_colors_fill(out, colors)
                out.append(line)
                started = False
            elif not started and line.startswith('static const char *colorn'):
                out.append(line)
                started = True
            else:
                out.append(line)
    outp = open(header, 'w+')
    outp.writelines(out)
    outp.flush()
    outp.close()


def set_gradient_colors(colors, f_lst, glist, overrides):
    l_colors = colors.copy()

    for i in range(0, len(overrides)):
        if overrides[i][1] != 'none':
            l_colors[overrides[i][0]] = l_colors[overrides[i][1]]
        else:
            l_colors[overrides[i][0]] = ''

    for i in range(0, len(f_lst)):
        c_multi_next = (i+1) / float(len(f_lst))
        c_multi = i / float(len(f_lst) - 1)

        for j in range(0, len(glist)):
            c_from = l_colors[glist[j][0]]
            c_to = l_colors[glist[j][1]]

            # val_grad_var = get_gradient(c_from, c_to, c_multi)
            # val_grad_var_n = get_gradient(c_from, c_to, c_multi_next)

            val_grad_var = glist[j][5](c_from, c_to, c_multi)
            val_grad_var_n = glist[j][5](c_from, c_to, c_multi_next)

            l_colors[glist[j][3]] = val_grad_var

            print(str(c_multi))

            if i < len(f_lst) - 1:
                l_colors[glist[j][4]] = val_grad_var_n
            else:
                l_colors[glist[j][4]] = l_colors[glist[j][2]]

        set_colors(l_colors, f_lst[i][0], f_lst[i][1])


def set_list_colors(colors, f_list, bg_var, bg_var_next, overrides,
                    overflow_clr):
    l_colors = colors.copy()

    for i in range(0, len(overrides)):
        if overrides[i][1] != 'none':
            l_colors[overrides[i][0]] = l_colors[overrides[i][1]]
        else:
            l_colors[overrides[i][0]] = ''

    for i in range(0, len(f_list)):
        bg = l_colors[f_list[i][2]]
        bg_n = ""

        if i+1 >= len(f_list):
            bg_n = l_colors[overflow_clr]
        else:
            bg_n = l_colors[f_list[i+1][2]]

        l_colors[bg_var] = bg
        l_colors[bg_var_next] = bg_n

        set_colors(l_colors, f_list[i][0], f_list[i][1])


def extractcolors(file):
    colors = {}

    with open(file) as f:
        for line in f:
            if line.startswith('color'):
                clr = line[0:line.index('#')].strip()
                clr = stripChar(clr, '\"')
                clr = stripChar(clr, '/')
                clr = clr.split('=', 1)

                if clr[1].startswith('$') and clr[1][1:] in colors:
                    colors[clr[0]] = colors[clr[1][1:]]
                else:
                    colors[clr[0]] = '#' + clr[1]
    return colors


def interpolate_basecolors(colors, mult):
    for i in range(0, 7):
        n_i = 8 + i
        n_i_str = 'color' + str(n_i) if n_i > 9 else 'color0' + str(n_i)
        i_str = 'color' + str(i) if i > 9 else 'color0' + str(i)
        colors[n_i_str] = get_colors_mult(colors[i_str], mult)


if __name__ == "__main__":
    ev = ''
    if 'BASE16_SHELL' in os.environ:
        ev = os.environ['BASE16_SHELL']
        clr = extractcolors(ev)
        # interpolate_basecolors(clr, 1.3)
        ovr = [
                ('color_foreground', 'color18'),
                ('color_separator', 'color18')
              ]
        # ovr = []
        set_colors(clr, i3_conf, 'i3')
        set_colors(clr, rofi_t, 'sh')
        set_st_colors(clr, st_config)
        grads = [
                 ('color02', 'color04', 'color18', 'color_background',
                  'color_background_next',
                  (lambda x, y, z: get_gradient(x, y, z)))
                 # ('color18', 'color15', 'color_foreground',
                 #  'color_foreground_next',
                 #  (lambda x, y, z: get_gradient(x, y,
                 #                  1.0 - get_distance(x, get_gradient(x, y, z)))))
                ]
        # set_gradient_colors(clr, i3_blocks, grads, ovr)
        set_list_colors(clr, i3_blocks, 'color_background',
                        'color_background_next', ovr, 'color18')
    exit(0)
