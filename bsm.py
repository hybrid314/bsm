#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2013 Kai Kratzer, Stuttgart, Germany; all rights
# reserved unless otherwise stated.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307 USA
#
#
# Sound playing machine using pygame
# Further information in the "README" and "COPYING" files.
# 
# Dependencies: apt-get install python-pygame
#

# directory listing
import glob
# system
import os
import sys
# parsing
import re
# random numbers
import random
# pygame (main window, sounds, events, timer)
import pygame
# calculations
import math

# pygame local variables
from pygame.locals import *

# Screen settings
width=1366
height=768
fullscreen = False

# Soundfile extensions
# not all is possible, look at the pygame documentation
sndfile_extensions = ['wav']

# Keybindings for the sounds (e.g. if no mouse/touch is available)
keybindings = { \
K_a: 'alkohol', \
K_b: 'bang', \
K_e: 'bier', \
K_q: 'dead', \
K_d: 'dynamit', \
K_f: 'fehlschuss', \
K_h: 'freude', \
K_g: 'gatling', \
K_s: 'general_store', \
K_i: 'indianer', \
K_n: 'kein_bang', \
K_k: 'kinnhaken', \
K_x: 'knapp', \
K_p: 'postkutsche', \
K_a: 'angry', \
K_w: 'shot_sheriff', \
K_r: 'talk', \
K_t: 'treffer', \
K_v: 'verwirrung', \
}

# timelimit for player's move. This is invoked, if "nextplayer" button is pressed
# speech announces 30, 20, 10, 5, 4, 3, 2, 1 seconds till end
player_timelimit = 30

# walk through subdirectories, collect sounds
def read_dir():
    bangdict = {}
    print "Reading directories..."
    for dname, dnames, fnames in os.walk('.'):
        dname = re.sub('.*/','',dname)
        if dname != '.' and dname != 'ambiente' and dname != 'speech' and dname != 'nextplayer' and dname != 'stopsound':
            soundfiles = []
            for ext in sndfile_extensions:
                soundfiles += glob.glob(dname + '/' + '*.' + ext)
            if len(soundfiles) > 0:
                bangdict[dname] = soundfiles

    print "done."
    return bangdict

# Choose random sound from folder
def random_sound(tkey):
    rndn = random.randint(0,len(bangsounds[tkey])-1)
    return bangsounds[tkey][rndn]

# Queue sound to player
def queue_sound(tsnd):
    print "Playing", tsnd
    sound = pygame.mixer.Sound(tsnd)
    sound.play()

# transform 2D index to linear
def get_linear_index(x,y):
    return x + y*nfieldx

# get y coordinate of linear index
def get_index_y(li):
    return li / nfieldx

# get x coordinate of linear index
def get_index_x(li):
    return li % nfieldx

# get field coordinates by mouse cursor position
def get_field(xm, ym):
    for xn in range(len(xborders)-1):
        if xm > xborders[xn] and xm <= xborders[xn+1]:
            break
    for yn in range(len(yborders)-1):
        if ym >= yborders[yn] and ym <= yborders[yn+1]:
            break

    return xn, yn

# get button name by mouse coordinates
def get_button(xm, ym):
    xn, yn = get_field(xm, ym)
    return bangbuttons[get_linear_index(xn,yn)]

# draw a small (white) exit corner in the bottom right field
def draw_exitcorner():
    pygame.draw.rect(window, cwhite, (width-exitcorner_size,height-exitcorner_size,width,height))

def buttoncaption(buttonname):
    return re.sub('_',' ',buttonname.capitalize())

# INIT SOUNDS
# dictionary of sounds and buttonnames
bangsounds = read_dir()
# alphabetically sorted buttons in array
bangbuttons = sorted(bangsounds, key=lambda key: bangsounds[key])
# add two buttons for nextplayer and stopsound
bangbuttons += ['nextplayer', 'stopsound']
nbuttons = len(bangbuttons)

# GAME WINDOW
pygame.init()
pygame.mixer.init()
pygame.font.init()

# fps clock
fpsClock = pygame.time.Clock()

# linewidth and 0.5*linewidth
lw = 4
lwh = int(round(0.5*lw))

# create window handler
if fullscreen:
    window = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
else:
    window = pygame.display.set_mode((width, height), DOUBLEBUF | HWSURFACE)

pygame.display.set_caption('Bang!soundmachine')

# set colors
cwhite = pygame.Color(255,255,255)
cblack = pygame.Color(0,0,0)
cred = pygame.Color(255,0,0)
cblue = pygame.Color(0,190,255)
cgreen = pygame.Color(0,255,150)
cyellow = pygame.Color(255,255,0)

# set color for buttons
colorbuttons = {\
'bang': cred, 'gatling': cred, 'kinnhaken': cred, \
'fehlschuss': cgreen, 'treffer': cgreen, \
'postkutsche': cyellow, 'general_store': cyellow, \
'kein_bang': cblue\
}

# size for the exit corner
exitcorner_size = 30

# initial window drawings
window.fill(cblack)
pygame.draw.line(window, cwhite, (0,0),(0,height),lw)
pygame.draw.line(window, cwhite, (0,0),(width,0),lw)
pygame.draw.line(window, cwhite, (0,height-lw+1),(width,height-lw+1),lw)
pygame.draw.line(window, cwhite, (width-lw+1,0),(width-lw+1,height),lw)
draw_exitcorner()

awidth = width - 2*lw
aheight = height - 2*lw
surface = (awidth) * (aheight)
ratio = float(awidth) / float(aheight)
fieldsurface = float(surface) / float(nbuttons)

# get field size with a certain edge ratio
fieldy = math.sqrt(fieldsurface / ratio)
fieldx = fieldy * ratio
fieldy = fieldy

testsurface = fieldx * fieldy

# higher number of fields in every direction
nfieldx = int(round(0.5+float(awidth)/fieldx))
nfieldy = int(round(0.5+float(aheight)/fieldy))

# try to avoid empty columns or rows
if (nfieldx - 1) * nfieldy >= nbuttons:
    nfieldx -= 1

if (nfieldy - 1) * nfieldx >= nbuttons:
    nfieldy -= 1

xborders = [0]
yborders = [0]

# draw borders of fields
if nfieldx > 0:
    dx = int(awidth / nfieldx)
    xoff = dx
    for i in range(nfieldx-1):
        xborders.append(xoff)
        pygame.draw.line(window, cwhite, (xoff-lwh,0),(xoff-lwh,height),lw)
        xoff += dx

if nfieldy > 0:
    dy = int(aheight / nfieldy)
    yoff = dy
    for i in range(nfieldy-1):
        yborders.append(yoff)
        pygame.draw.line(window, cwhite, (0,yoff-lwh),(width,yoff-lwh),lw)
        yoff += dy

xborders.append(width)
yborders.append(height)

# get maximum font size by testing if every button string fits into the fields
fontsize = 100
in_progress = True
print "Determining maximum possible font size..."
while in_progress:
    tfont = pygame.font.SysFont("Arial", fontsize)
    xtmp, ytmp = tfont.size(buttoncaption(bangbuttons[-1]))
    xvals = [xtmp]
    yvals = [ytmp]
    
    for i in range(nbuttons-1):
        xtmp, ytmp = tfont.size(buttoncaption(bangbuttons[i]))
        xvals.append(xtmp)
        yvals.append(ytmp)
    
    if max(xvals) >= dx or max(yvals) >= dy:
        fontsize -= 1
    else:
        in_progress = False

print "Done."

# Set buttons
for i in range(nbuttons):
    buttonname = bangbuttons[i]
    if buttonname in colorbuttons:
        tcolor = colorbuttons[buttonname]
    else:
        tcolor = cwhite
    ttext = tfont.render(buttoncaption(buttonname), True, tcolor)
    trect = ttext.get_rect()
    rx, ry = trect.bottomright
    # midpoint rectangle
    mrx = 0.5 * rx
    mry = 0.5 * ry
    
    ix = get_index_x(i)
    iy = get_index_y(i)
    
    xta = xborders[ix]
    xtb = xborders[ix+1]
    yta = yborders[iy]
    ytb = yborders[iy+1]
    # midpoint field
    mx = 0.5 * (xta + xtb)
    my = 0.5 * (yta + ytb)
    
    # move button text start corner to the correct coordinates
    window.blit(ttext,(int(mx-mrx),int(my-mry)))

# display the drawings
pygame.display.update()

# Startup sound
queue_sound('speech/hellouser.wav')

# frames per second
fps = 10
# frame counter
counter = 0
# second counter
seconds = 0
# timelimit starting value for user move
timelimit = False
#last_ifx = 0
#last_ify = 0

# MAIN LOOP
while True:
    # loop over events
    for event in pygame.event.get():
        # check for quit request
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # key pressed
        elif event.type == KEYDOWN:
            # check if in keybindings
            if event.key in keybindings:
                tbutton = keybindings[event.key]
                psnd = random_sound(tbutton)
                queue_sound(psnd)
            # fade out sounds if escape is pressed
            elif event.key == K_ESCAPE:
                pygame.mixer.fadeout(2000)

        # track mouse motion (fields could e.g. be highlighted)
        elif event.type == MOUSEMOTION:
            xm, ym = event.pos
            #ifx, ify = get_field(xm, ym)
            #if ifx != last_ifx or ify != last_ify:
            #    last_ifx = ifx
            #    last_ify = ify
            #    print ifx, ify
        # Mouse button is pressed
        elif event.type == MOUSEBUTTONDOWN:
            xm, ym = event.pos
            # hit exit corner, quit!
            if xm > width - exitcorner_size and ym > height - exitcorner_size:
                pygame.event.post(pygame.event.Event(QUIT))
            else:
                # try to play sound, otherwise fade out (e.g. if button without function is pressed)
                try:
                    cbutton = get_button(xm, ym)
                    if cbutton == 'stopsound':
                        pygame.mixer.fadeout(1000)
                    # start player timer
                    elif cbutton == 'nextplayer':
                        seconds = 0
                        timelimit = True
                    queue_sound(random_sound(cbutton))
                except Exception as e:
                    pygame.mixer.fadeout(2000)
                
    pygame.display.update()

    # increment fps counter
    counter += 1
    # if we have reached the number of fps, 1s has passed.
    if counter >= fps:
        # check for player timelimit
        if timelimit:
            # remaining seconds
            seconds_left = player_timelimit - seconds
            # play sounds
            if seconds_left > 0 and seconds_left <= 5:
                queue_sound('speech/' + str(seconds_left) + '_seconds.wav')
            elif seconds_left == 30:
                queue_sound('speech/30_seconds.wav')
            elif seconds_left == 20:
                queue_sound('speech/20_seconds.wav')
            elif seconds_left == 10:
                queue_sound('speech/10_seconds.wav')
            elif seconds_left == 0:
                timelimit = False
                queue_sound('speech/ba_endline.wav')

        counter = 0
        seconds += 1

    # let the clock tick
    fpsClock.tick(fps)

