import sqlite3, os, json, sys, js, asyncio, re, micropip, time, pyscript, io, glob, random
import xml.etree.ElementTree as ET
from base64 import b64encode, b64decode
from pyscript import document, when, display, window
from pyodide.http import pyfetch, open_url
from pyodide.ffi import create_proxy
from datetime import datetime, timedelta
from js import alert, prompt, localStorage, Hls, FileReader, console, Uint8Array, File


listItems = {}
listGroups = {}
urls = {}
htmlInput = { 'content': '<div class="content" id="content"></div>', 'header': '<div class="header"><video id="video"></video><div class="cols" id="cols"></div>', 'main': '<div class="main" id="main"></div>', 's2': '<div id="s2" class="sidebar hidden"><ul></ul></div>', 's1': '<div id="s1" class="sidebar hidden"><ul></ul></div>', 'li1': '<li id="%s"><i class="bx bx-movie-play bx-md"></i><span class="nav-item">%s</span></li>', 'li2': '<li id="%s"><span class="nav-item">%s</span></li>', 'con': [ '<div class="row" id="_r%s_">', '<div class="card" id="_r%s_c%s_"><div class="container" id="_i%s_"><img src="%s" alt="" id="%s"><div class="title" id="%s">%s</div></div></div>', '</div>' ], 'head': '<div class="title">%s</div><div class="sub-title">%s - %s</div><div class="details" style="flex-grow: 1;">%s</div>', 'head1': '<div class="title">Test</div><div class="sub-title">Sub <div class="progress-bar"><span class="bar"><span class="progress" style="width: 50px;"></span></span></div></div><div class="details" style="flex-grow: 1;">Details</div>' }
htmlOutput = { 'html': '<li id="Settings" py-click="onclick_s1"><i class="bx bx-cog bx-md"></i><span class="nav-item">Settings</span></li><li id="Exit"><i class="bx bx-exit bx-md"></i><span class="nav-item">Logout</span></li>', 'Settings': { 'html': '<li id="list"><span class="nav-item">Lists</span></li>', 'list': { 'html': '<div class="content" id="settings"><div class="list"><div class="item" id="expandable"><div class="col head expand"><b>Add New List</b></div><div class="col"><button class="b0"><b>v</b></button></div></div><div class="hidden" id="hide"><div class="item"><div class="col expand"><div class="row head"><b>M3u8 Liste</b></div><div class="row"><input class="w3" placeholder="List Name ..."> <input class="w5" placeholder="List Url ..."></div></div><div class="col"><button class="b1">Add</button></div></div><div class="item"><div class="col expand"><div class="row head"><b>Xtream Account</b></div><div class="row"><input class="w3" placeholder="List Name ..."> <input class="w5" placeholder="Server Url ..."></div><div class="row"><input class="w3" placeholder="User Name ..."> <input class="w3" placeholder="User Password ..."></div></div><div class="col"><button class="b1">Add</button></div></div></div><div class="item"><div class="col head expand"><b>Edit User Lists</b></div><div class="col"><button class="b0"><b>v</b></button></div></div><div class="hidden" id="hide"></div></div></div>' } } }
epgOutput = {}
keyCodes = { '8': 'Del', '9': 'Tab', '13': 'Enter', '16': 'Cap', '17': 'Strg', '18': 'Alt', '19': 'Pause', '27': 'Esc', '32': 'Space', '33': 'PageUp', '34': 'PageDown', '35': 'Ende', '36': 'Pos1', '37': 'Left', '38': 'Up', '39': 'Right', '40': 'Down', '45': 'Einfg', '46': 'Entf', '48': '0', '49': '1', '50': '2', '51': '3', '52': '4', '53': '5', '54': '6', '55': '7', '56': '8', '57': '9', '77': 'm', '225': 'AltGr', '403': 'Red', '404': 'Green', '405': 'Yellow', '406': 'Blue', '412': '<<', '413': 'Stop', '415': 'Play', '416': 'Rec', '417': '>>', '427': 'CH-', '428': 'CH+', '447': 'Vol-', '448': 'Vol+', '449': 'Mute', '457': 'Info', '10009': 'Back', '10073': 'CH-List', '10135': 'Tools', '10190': 'Pre-CH', '10225': 'Search', '10252': 'Play_Pause', '65376': 'Done', '65385': 'Cancel' }
Pause = False
Fullscreen = False
con = wsig = None


def onclick_s1(event):
    #event.target.id
    body = document.querySelector("body")
    if (actives := document.querySelectorAll(".active")):
        for act in actives:
            act.classList.remove('active')
    s1 = body.querySelector('#s1')
    if not (s1.classList.contains('active')): s1.classList.add('active')
    if not (s1i := document.getElementById(event.target.id)):
        console.log(event.target.id)
        console.log('[s1i][click]Error!')
        return
    if not (s1i.classList.contains('active')): s1i.classList.add('active')
    checkHtml()
    s1.classList.remove('active')
    s1i.classList.remove('active')
    s1i.classList.add('selected')
    s2 = body.querySelector('#s2')
    if not (s2i := body.querySelector('.actived')):
        s2ii = body.querySelectorAll('#s2 li')
        s2i = s2ii[0]
    if (s2.classList.contains('hidden')): s2.classList.remove('hidden')
    s2.classList.add('active')
    if (s2i.classList.contains('actived')): s2i.classList.remove('actived')
    s2i.classList.add('active')
    checkHtml()


@when("keydown", "body")
async def keyHandler(e):
    global keyCodes
    if str(e.keyCode) in keyCodes:
        keyEvent = keyCodes[str(e.keyCode)]
        eventHandler(keyEvent)


def eventHandler(keyEvent):
    global htmlOutput, Pause, Fullscreen
    selected1 = selected2 = selected3 = active1 = active2 = active3 = actived1 = actived2 = actived3 = None
    log = ''
    body = document.querySelector("body")
    if not (m := body.querySelector('.main')): log += '[main]'
    if not (s1 := body.querySelector('#s1')): log += '[s1]'
    if not (s2 := body.querySelector('#s2')): log += '[s2]'
    if not (c := m.querySelector('#content')):
        if not (c := m.querySelector('#settings')):
            log += '[content]'
    if not (body.classList.contains('loaded')) or not (actives := document.querySelectorAll(".active")):
        initMenu()
    if str(len(actives)) == "2":
        active1 = str(actives[0].id)
        active2 = str(actives[1].id)
    elif len(actives) > 0:
        for act in actives:
            if str(act.id) == 's1' or str(act.id) == 's2' or str(act.id) == 'content' or str(act.id) == 'settings': active1 = str(act.id)
            elif active1 and not active2: active2 = str(act.id)
            elif active1 and active2 and not active3: active3 = str(act.id)
            else: break
    if s1:
        t = '[s1'
        if (s1s := s1.querySelector('.selected')): selected1 = str(s1s.id)
        else: t += 's'
        if (s1a := s1.querySelector('.actived')): actived1 = str(s1a.id)
        else: t += 'a'
        if not (s1i := s1.querySelector('.active')): t += 'i'
        if not t == '[s1': log += t + ']'
    if s2:
        t = '[s2'
        if (s2s := s2.querySelector('.selected')): selected2 = str(s2s.id)
        else: t += 's'
        if (s2a := s2.querySelector('.actived')): actived2 = str(s2a.id)
        else: t += 'a'
        if not (s2i := s2.querySelector('.active')): t += 'i'
        if not t == '[s2': log += t + ']'
    if c:
        t = '[c'
        if (cs := c.querySelector('.selected')): selected3 = str(cs.id)
        else: t += 's'
        if (ca := c.querySelector('.actived')): actived3 = str(ca.id)
        else: t += 'a'
        if not (ci := c.querySelector('.active')): t += 'i'
        if not t == '[c': log += t + ']'
    if not log == '': console.log('Not found: ' + log)
    if str(keyEvent) == 'Play':
        vid = document.getElementById('video')
        vid.play()
        Pause = False
    elif str(keyEvent) == 'Pause':
        vid = document.getElementById('video')
        vid.pause()
        Pause = True
    elif str(keyEvent) == 'Play_Pause':
        vid = document.getElementById('video')
        if Pause:
            vid.play()
            Pause = False
        else:
            vid.pause()
            Pause = True
    elif str(keyEvent) == 'Enter':
        console.log(active1)
        if Fullscreen: return
        elif active1 == 's1':
            if active2 in htmlOutput:
                html = htmlOutput[active2]['html']
                if not (s2i := body.querySelector('.actived')):
                    if not (s2 := body.querySelector('#s2 ul')):
                        window.console.log('[Sidebar][2][ul][Error!]')
                        return
                    s2.innerHTML = ''.join(html)
                s1 = body.querySelector('#'+active1)
                s1i = body.querySelector('#'+active2)
                s1i.classList.remove('active')
                s1i.classList.add('selected')
                s1.classList.remove('active')
                s2 = body.querySelector('#s2')
                if not (s2i := body.querySelector('.actived')):
                    s2ii = body.querySelectorAll('#s2 li')
                    s2i = s2ii[0]
                if (s2.classList.contains('hidden')): s2.classList.remove('hidden')
                if not (s2.classList.contains('active')): s2.classList.add('active')
                if (s2i.classList.contains('actived')): s2i.classList.remove('actived')
                if not (s2i.classList.contains('active')): s2i.classList.add('active')
            checkHtml()
        elif active1 == 's2':
            if (con := body.querySelector('.main #content')):
                if not (ci := con.querySelector('.actived')):
                    if not (ci := con.querySelector('#_r0_c0_')):
                        window.console.log('[Card][Error!]')
                        return
            elif (con := body.querySelector('.main #settings')):
                console.log('JA')
            s2 = body.querySelector('#'+active1)
            s2i = s2.querySelector('#'+active2)
            s2.classList.remove('active')
            s2.classList.add('activated')
            s2i.classList.remove('active')
            s2i.classList.add('selected')
            con.classList.add('active')
            if (ci.classList.contains('actived')): ci.classList.remove('actived')
            ci.classList.add('active')
        elif active1 == 'content':
            global urls
            vid = document.getElementById('video')
            con = body.querySelector('#'+active1)
            ci = con.querySelector('#'+active2)
            if (ci.classList.contains('selected')):
                if not (vid.classList.contains('fullscreen')):
                    vid.classList.add('fullscreen')
                    Fullscreen = True
            else:
                if not (cic := con.querySelector('#'+active2+' .container')):
                    window.console.log('[Active][Item][Container][Error!]')
                    return
                i = re.sub('_.*', '', re.sub('.*_i', '', cic.id))
                if not (s2s := body.querySelector('#s2 .selected')):
                    window.console.log('[Sidebar][2][Selected][Error!]')
                    return
                url = urls[str(s2s.id)][int(i)]
                hls = Hls.new()
                hls.loadSource(url)
                hls.attachMedia(vid)
                if not (ci.classList.contains('selected')): ci.classList.add('selected')
                vid.play()

    elif str(keyEvent) == 'Back' or str(keyEvent) == 'Esc':
        if Fullscreen:
            vid = document.getElementById('video')
            if (vid.classList.contains('fullscreen')):
                vid.classList.remove('fullscreen')
                Fullscreen = False
        elif active1 == 's2':
            s1 = body.querySelector('#s1')
            s2 = body.querySelector('#s2')
            if not (s1s := body.querySelector('#s1 .selected')):
                window.console.log('[Sidebar][1][Selected][Error!]')
                return
            if not (s2i := body.querySelector('#s2 .active')):
                window.console.log('[Sidebar][2][Item][Error!]')
                return
            s2i.classList.remove('active')
            s2i.classList.add('actived')
            s2.classList.remove('active')
            s2.classList.add('hidden')
            s1.classList.add('active')
            s1s.classList.remove('selected')
            s1s.classList.add('active')
        elif active1 == 'content':
            s2 = body.querySelector('#s2')
            ci = body.querySelector('#'+active2)
            cm = body.querySelector('#'+active1)
            if not (s2s := body.querySelector('#s2 .selected')):
                window.console.log('[Sidebar][2][Selected][Error!]')
                return
            ci.classList.remove('active')
            ci.classList.add('actived')
            cm.classList.remove('active')
            if (s2.classList.contains('activated')): s2.classList.remove('activated')
            s2.classList.add('active')
            s2s.classList.remove('selected')
            s2s.classList.add('active')
    elif str(keyEvent) == 'Down':
        if Fullscreen: return
        elif active1 == 'content':
            if not '_r' in active2 or not '_c' in active2:
                window.console.log('[Content][Card][ID][Error!]')
                return
            r = int(re.sub('_.*', '', re.sub('.*_r', '', active2)))
            c = int(re.sub('_.*', '', re.sub('.*_c', '', active2)))
            cm = body.querySelector('#'+active1)
            ci = body.querySelector('#'+active2)
            if not (cn := cm.querySelector('#_r'+str(r+1)+'_c'+str(c)+'_')):
                if not (cn := cm.querySelector('#_r'+str(0)+'_c'+str(c)+'_')): return
            ci.classList.remove('active')
            cn.classList.add('active')
            cn.scrollIntoView()
        else:
            items = body.querySelectorAll('#'+active1+' li')
            x = 0
            for item in items:
                if (item.classList.contains('active')): break
                x += 1
            items[x].classList.remove('active')
            if x < int(len(items) - 1): items[int(x+1)].classList.add('active')
            else: items[int(0)].classList.add('active')
            if active1 == 's2':
                if not (s2i := body.querySelector('#s2 .active')): window.console.log('[Sidebar][2][Item][Error!]')
                if not (s1s := body.querySelector('#s1 .selected')): window.console.log('[Sidebar][1][Selected][Error!]')
            checkHtml()
    elif str(keyEvent) == 'Up':
        if Fullscreen: return
        elif active1 == 'content':
            if not '_r' in active2 or not '_c' in active2:
                window.console.log('[Content][Card][ID][Error!]')
                return
            r = int(re.sub('_.*', '', re.sub('.*_r', '', active2)))
            c = int(re.sub('_.*', '', re.sub('.*_c', '', active2)))
            cm = body.querySelector('#'+active1)
            ci = body.querySelector('#'+active2)
            ca = body.querySelectorAll('.card')
            cl = ca[int(len(ca)-1)]
            r2 = int(re.sub('_.*', '', re.sub('.*_r', '', cl.id)))
            if r > 0:
                if not (cn := cm.querySelector('#_r'+str(r-1)+'_c'+str(c)+'_')): return
            elif r == 0:
                if not (cn := cm.querySelector('#_r'+str(r2)+'_c'+str(c)+'_')):
                    if not (cn := cm.querySelector('#_r'+str(r2-1)+'_c'+str(c)+'_')): return
            ci.classList.remove('active')
            cn.classList.add('active')
            cn.scrollIntoView()
        else:
            items = body.querySelectorAll('#'+active1+' li')
            x = 0
            for item in items:
                if (item.classList.contains('active')): break
                x += 1
            items[x].classList.remove('active')
            if x > 0: items[int(x-1)].classList.add('active')
            else: items[int(len(items)-1)].classList.add('active')
            if active1 == 's2':
                if not (s2i := body.querySelector('#s2 .active')): window.console.log('[Sidebar][2][Item][Error!]')
                if not (s1s := body.querySelector('#s1 .selected')): window.console.log('[Sidebar][1][Selected][Error!]')
            checkHtml()
    elif str(keyEvent) == 'Right':
        if Fullscreen: return
        elif active1 == 'content':
            if not '_r' in active2 or not '_c' in active2:
                window.console.log('[Content][Card][ID][Error!]')
                return
            r = int(re.sub('_.*', '', re.sub('.*_r', '', active2)))
            c = int(re.sub('_.*', '', re.sub('.*_c', '', active2)))
            cm = body.querySelector('#'+active1)
            ci = body.querySelector('#'+active2)
            if c < 9:
                if not (cn := cm.querySelector('#_r'+str(r)+'_c'+str(c+1)+'_')):
                    if not (cn := cm.querySelector('#_r'+str(r+1)+'_c'+str(0)+'_')):
                        if not (cn := cm.querySelector('#_r'+str(0)+'_c'+str(0)+'_')): return
            elif c == 9:
                if not (cn := cm.querySelector('#_r'+str(r+1)+'_c'+str(0)+'_')):
                   if not (cn := cm.querySelector('#_r'+str(0)+'_c'+str(0)+'_')): return
            ci.classList.remove('active')
            cn.classList.add('active')
            cn.scrollIntoView()
    elif str(keyEvent) == 'Left':
        if Fullscreen: return
        elif active1 == 'content':
            if not '_r' in active2 or not '_c' in active2:
                window.console.log('[Content][Card][ID][Error!]')
                return
            r = int(re.sub('_.*', '', re.sub('.*_r', '', active2)))
            c = int(re.sub('_.*', '', re.sub('.*_c', '', active2)))
            cm = body.querySelector('#'+active1)
            ci = body.querySelector('#'+active2)
            ca = body.querySelectorAll('.card')
            cl = ca[int(len(ca)-1)]
            if c > 0:
                if not (cn := cm.querySelector('#_r'+str(r)+'_c'+str(c-1)+'_')): return
            elif c == 0 and r == 0: cn = cl
            elif c == 0 and r > 0:
                if not (cn := cm.querySelector('#_r'+str(r-1)+'_c'+str(9)+'_')): return
            ci.classList.remove('active')
            cn.classList.add('active')
            cn.scrollIntoView()
    pass


def initMenu():
    body = document.querySelector("body")
    if not (sidebar := body.querySelector("#s1")): window.console.log('[Sidebar][1][Error!]')
    if (sidebar.classList.contains('hidden')): sidebar.classList.remove('hidden')
    if not (sidebar.classList.contains('active')):
        items = sidebar.querySelectorAll("li")
        if len(items) > 0:
            sidebar.classList.add('active')
            items[0].classList.add('active')
    if not (test := body.querySelector("#s2")): window.console.log('[Sidebar][2][Test][Error!]')
    if (test.classList.contains('active')): test.classList.remove('active')
    if not (test.classList.contains('hidden')): test.classList.add('hidden')
    if (test := body.querySelector(".content")):
        if (test.classList.contains('active')): test.classList.remove('active')
    if not (body.classList.contains('loaded')): body.classList.add('loaded')
    if (loader := body.querySelector(".loader")):
        if (loader.classList.contains('is-active')): loader.classList.remove('is-active')
    checkHtml()

def checkHtml():
    global htmlInput, htmlOutput
    body = document.querySelector("body")
    active1 = active2 = active3 = None
    if (actives := document.querySelectorAll(".active")):
        for act in actives:
            if str(act.id) == 's1' or str(act.id) == 's2' or str(act.id) == 'content' or str(act.id) == 'settings': active1 = str(act.id)
            elif active1 and not active2: active2 = str(act.id)
            elif active1 and active2 and not active3: active3 = str(act.id)
            else: break
    if active1 == 's1':
        if active2 in htmlOutput:
            sidebar = document.querySelector("#s2")
            ul = sidebar.querySelector("ul")
            ul.innerHTML = htmlOutput[active2]['html']
    elif active1 == 's2':
        sidebar = document.querySelector("#s1")
        if not (s1s := sidebar.querySelector('.selected')): console.log('[s1s]Error!')
        main = document.querySelector("#main")
        if not str(s1s.id) == 'Settings':
            if not (head := main.querySelector('#header')):
                main.innerHTML = htmlInput['header']
            if not (content := main.querySelector('#content')):
                main.innerHTML += htmlInput['content']
        if str(s1s.id) in htmlOutput:
            if active2 in htmlOutput[str(s1s.id)]:
                if not str(s1s.id) == 'Settings':
                    content = main.querySelector('#content')
                    content.innerHTML = htmlOutput[str(s1s.id)][active2]['html']
                else:
                    main.innerHTML = htmlOutput[str(s1s.id)][active2]['html']


def menuBuilder():
    global htmlOutput
    sidebar = document.querySelector("#s1")
    ul = sidebar.querySelector("ul")
    ul.innerHTML = htmlOutput['html']
    sidebar = document.querySelector("#s1")
    items = sidebar.querySelectorAll("li")
    if len(items) > 0:
        if str(items[0].id) in htmlOutput:
            sidebar = document.querySelector("#s2")
            ul = sidebar.querySelector("ul")
            ul.innerHTML = htmlOutput[str(items[0].id)]['html']
    initMenu()


def htmlBuilder(lid):
    global con, htmlOutput, htmlInput
    li1 = htmlInput['li1']
    li2 = htmlInput['li2']
    conn = {}
    conn['b'] = htmlInput['con'][0]
    conn['i'] = htmlInput['con'][1]
    conn['a'] = htmlInput['con'][2]
    cur = con.cursor()
    r = {}
    c = {}
    if (List := cur.execute('SELECT * FROM lists WHERE id="'+str(lid)+'"').fetchone()): m3u8 = List['name']
    if not m3u8 in htmlOutput:
        htmlOutput['html'] = li1 %(m3u8, m3u8) + htmlOutput['html']
        htmlOutput[m3u8] = { 'html': '' }
        for row in cur.execute('SELECT * FROM channels WHERE lid="' + str(lid) + '" ORDER BY name'):
            group = str(row['group'])
            if not group in r: r[group] = 0
            if not group in c: c[group] = 0
            if not group in htmlOutput[m3u8]:
                htmlOutput[m3u8]['html'] += li2 %(group, group)
                htmlOutput[m3u8][group] = { 'html': '' }
            if str(c[group]) == "0": htmlOutput[m3u8][group]['html'] += conn['b'] % str(r[group])
            if row['logo'] == None or row['logo'] == '': logo = "https://raw.githubusercontent.com/Mastaaa1987/vxparser/tizen/tizen/vplayer.png"
            else: logo = row['logo']
            if not row['tid'] == None and not row['tid'] == '': tid = row['tid']
            else: tid = ''
            htmlOutput[m3u8][group]['html'] += conn['i'] %(str(r[group]), str(c[group]), str(row['id']), str(logo), str(tid), str(group), str(row['name']))
            if str(c[group]) == "9":
                htmlOutput[m3u8][group]['html'] += conn['a']
                r[group] += 1
                c[group] = 0
            else: c[group] += 1
        reLoad()


def epgBuilder():
    global con, epgOutput, htmlInput
    cur = con.cursor()

    epg_channels = []
    epg_ids = {}
    for row in cur.execute('SELECT * FROM epgs ORDER BY id'):
        if not row['tid'] == None and not row['tid'] == '':
            epg_channels.append(str(row['tid']))
            epg_ids[str(row['tid'])] = str(row['rid'])

    epgOutput = {}
    head = htmlInput['head']
    for epg in epg_channels:
        rid = epg_ids[str(epg)]
        if (test := cur.execute('SELECT * FROM epg WHERE cid="'+str(rid)+'" AND start < "'+str(int(time.time()))+'" AND end > "'+str(int(time.time()))+'"').fetchone()):
            epgOutput[str(rid)] = { 'html': '' }
            epgOutput[str(rid)]['end'] = int(test['end'])
            title = re.sub('b\'', '\'', str(b64decode(re.sub('b\'', '\'', test['title'])))).encode('ascii', 'ignore').decode('ascii')
            desc = re.sub('b\'', '\'', str(b64decode(re.sub('b\'', '\'', test['desc'])))).encode('ascii', 'ignore').decode('ascii')
            console.log(str(desc))
            #epgOutput[str(rid)]['html'] += head %(, str(datetime.fromtimestamp(int(test['start'])).strftime("%H:%M")), str(datetime.fromtimestamp(int(test['end'])).strftime("%H:%M")), b64decode(str(test['desc']).encode('utf-8')))
            if (test := cur.execute('SELECT * FROM epg WHERE cid="'+str(rid)+'" AND start > "'+str(int(time.time()))+'" ORDER BY start').fetchone()):
                epgOutput[str(rid)]['start'] = int(test['start'])
                #epgOutput[str(rid)]['html'] += head %(b64decode(str(test['title']).encode('utf-8')), str(datetime.fromtimestamp(int(test['start'])).strftime("%H:%M")), str(datetime.fromtimestamp(int(test['end'])).strftime("%H:%M")), b64decode(str(test['desc']).encode('utf-8')))
    console.log(str(epgOutput))


def parse(m3u8_name, m3u8):
    global listItems
    global listGroups
    if m3u8_name not in listGroups:
        listGroups[m3u8_name] = {}
    lines = m3u8.split("\n")
    items = []
    x = 0
    for line in lines:
        if '#EXTINF:' in str(line):
            tvgname = group = logo = name = tvgid = None
            if 'tvg-name="' in str(line) and not 'tvg-name=""' in str(line):
                tvgname = re.sub('".*', '', re.sub('.*tvg-name="', '', str(line)))
            if 'group-title="' in str(line) and not 'group-title=""' in str(line):
                group = re.sub('".*', '', re.sub('.*group-title="', '', str(line)))
            if 'tvg-logo="' in str(line) and not 'tvg-logo=""' in str(line):
                logo = re.sub('".*', '', re.sub('.*tvg-logo="', '', str(line)))
            if 'tvg-id="' in str(line) and not 'tvg-id=""' in str(line):
                tvgid = re.sub('".*', '', re.sub('.*tvg-id="', '', str(line)))
            name = re.sub('.*,', '', str(line))
        elif 'http://' in str(line) or 'https://' in str(line):
            url = str(line)
            item = { 'tvgname': tvgname, 'group': group, 'logo': logo, 'tvgid': tvgid, 'name': name, 'url': url }
            items.append(item)
            if not group is None and group not in listGroups[m3u8_name]:
                listGroups[m3u8_name][group] = []
            if not group is None:
                listGroups[m3u8_name][group].append(item)
    listItems[m3u8_name] = items
    htmlBuilder()


async def main():
    if not (config := localStorage.getItem("vxConfig")):
        url = prompt("M3U8 URL?", "http://127.0.0.1:8081/Germany_hls.m3u8")
        name = prompt("Name?", "Germany")
        if url and name:
            item = { "name": name, "url": url }
            localStorage.setItem("vxConfig", json.dumps(item))
    if (config := localStorage.getItem("vxConfig")):
        j = json.loads(config)
    try:
        response = await pyfetch(str('http://0.0.0.0:8081/Germany.m3u8'))
        if response.ok:
            data = await response.text()
            parse(str(j['name']), data)
    except:
        return


def temp():
    lines = '<div class="list">'

    lines += '<div class="item" id="expandable"><div class="col head expand"><b>Add New List</b></div><div class="col"><button class="b0"><b>v</b></button></div></div>'
    lines += '<div class="expandable hidden">'
    lines += '<div class="item"><div class="col expand"><div class="row head"><b>M3u8 Liste</b></div><div class="row"><input class="w3" placeholder="List Name ..."> <input class="w5" placeholder="List Url ..."></div></div><div class="col"><button class="b1">Add</button></div></div>'
    lines += '<div class="item"><div class="col expand"><div class="row head"><b>Xtream Account</b></div><div class="row"><input class="w3" placeholder="List Name ..."> <input class="w5" placeholder="Server Url ..."></div><div class="row"><input class="w3" placeholder="User Name ..."> <input class="w3" placeholder="User Password ..."></div></div><div class="col"><button class="b1">Add</button></div></div>'
    lines += '</div>'

    lines += '<div class="item"><div class="col head expand"><b>Edit User Lists</b></div><div class="col"><button class="b0"><b>^</b></button></div></div>'
    lines += '<div class="expandable hidden">'
    lines += '<div class="item"><div class="col expand"><div class="row head"><b>M3u8 Liste</b></div><div class="row"><input class="w3" placeholder="List Name ..."> <input class="w5" placeholder="List Url ..."></div></div><div class="col"><button class="b1">Add</button></div></div>'
    lines += '<div class="item"><div class="col expand"><div class="row head"><b>Xtream Account</b></div><div class="row"><input class="w3" placeholder="List Name ..."> <input class="w5" value="Server Url ..."></div><div class="row"><input class="w3" placeholder="User Name ..."> <input class="w3" placeholder="User Password ..."></div></div><div class="col"><button class="b1_0">Edit</button><button class="b1_1">Delete</button></div></div>'
    lines += '</div>'

    lines += '</div>'


def checkLists():
    global con
    cur = con.cursor()
    if not (test := cur.execute('SELECT * FROM lists WHERE type="VAVOO"').fetchone()):
        asyncio.ensure_future(getVavoo())
    elif test['last'] == '' or test['last'] == None:
        asyncio.ensure_future(getVavoo())
    else:
        console.log(str(test['last']))
        htmlBuilder(test['id'])
    if not (test := cur.execute('SELECT * FROM epg WHERE start < "'+str(int(time.time()))+'" AND end > "'+str(int(time.time()))+'"').fetchone()):
        asyncio.ensure_future(getEpg())
    else: epgBuilder()


def saveDB():
    global con
    con.commit()
    con.close()
    ifile = open('/home/pyodide/database.db','rb')
    bytes_list = bytearray(ifile.read())
    my_bytes = io.BytesIO(bytes_list)
    db_file = File.new([Uint8Array.new(my_bytes.getvalue())], "vxplayer.db")
    window.App.writeFileToFS(db_file)
    con = sqlite3.connect('database.db')
    unicode = str
    con.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
    con.text_factory = lambda x: unicode(x, errors='ignore')
    console.log('[DB][Saved]')


def createDB():
    con = sqlite3.connect('sql.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS lists ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "type" TEXT, "name" TEXT, "url" TEXT, "username" TEXT, "password" TEXT, "last" TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS channels ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "lid" INTEGER, "name" TEXT, "group" TEXT, "url" TEXT, "logo" TEXT, "tname" TEXT, "tid" TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS epg ( "id" INTEGER PRIMARY KEY AUTOINCREMENT, "cid" TEXT, "start" INTEGER, "end" INTEGER, "title" TEXT, "desc" TEXT, "lang" TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS epgs ( "id" INTEGER PRIMARY KEY AUTOINCREMENT, "rid" TEXT, "mid" TEXT, "mn" TEXT, "tid" TEXT, "tn" TEXT, "display" TEXT, "ol" TEXT, "ml" TEXT, "tl" TEXT, "name" TEXT, "name1" TEXT, "name2" TEXT, "name3" TEXT, "name4" TEXT, "name5" TEXT)')
    con.commit()
    epg = [
        (None, "123.tv.de", "4724", "1-2-3.tv", "123TV", "123.tv", "1-2-3.tv", "http://ngiss.t-online.de/cm1s/media/c997fed51bd331bc260a8cadeb773a3d036335e8.png", "http://ngiss.t-online.de/cm1s/media/ca0c611992e1d587d76fab310e74ca4e32ff69ab.png", "http://live.tvspielfilm.de/static/images/channels/large/123TV.png", "123 TV", "1.2.3 TV", None, None, None, None),
        (None, "13thStreet.de", "471", "13TH STREET (Sky)", "13TH", "13th Street Universal", "13th Street", "http://ngiss.t-online.de/cm1s/media/a8e6a82760b56428170e316932f38fabeb0814db.png", "http://ngiss.t-online.de/cm1s/media/668cd4d06f6981b82841f40fad42bc350babb056.png", "http://live.tvspielfilm.de/static/images/channels/large/13TH.png", "13TH STREET", None, None, None, None, None),
        (None, "3sat.de", "392", "3sat", "3SAT", "3sat", "3sat", "http://ngiss.t-online.de/cm1s/media/cb4ad5071a81df9a8f926ab737dd81934a3f3c43.png", "http://ngiss.t-online.de/cm1s/media/f0fc63107fddc5c72d70a64f90f9672710e3a3d9.png", "http://live.tvspielfilm.de/static/images/channels/large/3SAT.png", "3SAT", "3 SAT", None, None, None, None),
        (None, "AllgauTV.de", "448", "allgäu.tv", None, None, "Allgäu TV", "http://ngiss.t-online.de/cm1s/media/1d733842aa82ebca90710f51fec8b8f35922ae00.png", "http://ngiss.t-online.de/cm1s/media/d37488ac6d2572b3cda8b5abc35f2ef632f46d8d.png", None, None, None, None, None, None, None),
        (None, "AnimalPlanet.de", "105", "Animal Planet", "APLAN", "Animal Planet", "Animal Planet", "http://ngiss.t-online.de/cm1s/media/5255ebd8c1bfed40d33eff7bc066c6a61c7adab4.png", "http://ngiss.t-online.de/cm1s/media/cd0ca6f68c634ba2fd4ce665043f3cefdd1c1c9d.png", "http://live.tvspielfilm.de/static/images/channels/large/APLAN.png", "ANIMAL PLANET", "PLANET", None, None, None, None),
        (None, "Anixe.de", "452", "ANIXE+", "ANIXE", "ANIXE", "Anixe HD", "http://ngiss.t-online.de/cm1s/media/a39367d3874a697055b11ea159da1e528c79bc69.png", "http://ngiss.t-online.de/cm1s/media/7d936048c94ca83281a61951170b5ad0da756584.png", "http://live.tvspielfilm.de/static/images/channels/large/ANIXE.png", "ANIXE", "ANIXE+", None, None, None, None),
        (None, "AnixeSerie.de", "4777", "ANIXE HD Serie", None, None, "Anixe Serie HD", "http://ngiss.t-online.de/cm1s/media/6dad0a5ad793821b149d1fc6bfd4168e6d128a2d.png", "http://ngiss.t-online.de/cm1s/media/f105ac8c8e8dbede59277c3b2019c65ea1ecfc95.png", None, "ANIXE SERIE", "ANIXE SERIES", "SONY ANIXE", None, None, None),
        (None, "ARD-alpha.de", "479", "ARD-alpha", "ALPHA", "ARD alpha", "ARD-alpha", "http://ngiss.t-online.de/cm1s/media/ca7b82627f3ebabc7c3a37b306b621721bbdc91e.png", "http://ngiss.t-online.de/cm1s/media/4f1286373cd3362649d2e4ae1692ab8a360bf773.png", "http://live.tvspielfilm.de/static/images/channels/large/ALPHA.png", "ARD ALPHA", None, None, None, None, None),
        (None, "ARTE.de", "394", "ARTE", "ARTE", "ARTE", "arte", "http://ngiss.t-online.de/cm1s/media/8421f189118991ab7b5d1bb1a749cf8eca1b0501.png", "http://ngiss.t-online.de/cm1s/media/a94bb4917f279b02cb739e788c18f38a009f95a0.png", "http://live.tvspielfilm.de/static/images/channels/large/ARTE.png", "ARTE", None, None, None, None, None),
        (None, "ATV.de", "161", "a.tv", None, None, "ATV", "http://ngiss.t-online.de/cm1s/media/62acac335cc4c018f85314654615d42b81d4541c.png", "http://ngiss.t-online.de/cm1s/media/ecd02c711e2a96d79702ef779035c9b03ecb5811.png", None, "ATV", None, None, None, None, None),
        (None, "AutoMotorSport.de", "108", "auto motor und sport", "AMS", "Auto Motor Sport", "Auto Motor und Sport", "http://ngiss.t-online.de/cm1s/media/eafee48faac5801ba1be0a006b07b1dedbe4cc8b.png", "http://ngiss.t-online.de/cm1s/media/8ffbb0a95849b6c7af04aeaea5c2e1680c6cb0ad.png", "http://live.tvspielfilm.de/static/images/channels/large/AMS.png", "AUTO MOTOR SPORT", "AUTO MOTO SPORT", "AUTO MOTOR UND SPORT", None, None, None),
        (None, "AXNBlack.de", "110", "AXN Black", "AXN", "AXN", "AXN", "http://ngiss.t-online.de/cm1s/media/c4a0608099c553e609d54d568cad48779ff9b639.png", "http://ngiss.t-online.de/cm1s/media/df6a8f84c2ecbe26b090e37b782db46b9d98b1bb.png", "http://live.tvspielfilm.de/static/images/channels/large/AXN.png", "AXN", "SONY AXN", "SONY ANIXE", None, None, None),
        (None, "BabyTV.de", "109", "Baby TV", None, None, "Baby TV", "http://ngiss.t-online.de/cm1s/media/b4541398d4daef82bca028fb931fc9686ef3ba8b.png", "http://ngiss.t-online.de/cm1s/media/5ba6b3a95fbbbce05e3b62e45196771dbf2fe33e.png", None, "BABY TV", None, None, None, None, None),
        (None, "BBCEntertainment.de", "454", "BBC News", None, None, "BBC entertainment", "http://ngiss.t-online.de/cm1s/media/b9bd11f0b4072a851e7670eebe332bda1bd974c5.png", "http://ngiss.t-online.de/cm1s/media/f41b3e216d38d542dd49f4e3d0f1d21d87dd43cb.png", None, None, None, None, None, None, None),
        (None, "BeateUhse.de", "107", "Beate-Uhse.TV (Sky)", None, None, "Beate-Uhse.TV", "http://ngiss.t-online.de/cm1s/media/6b2cb297d048f60a2f22c8b42a74daaa2c7fd3e2.png", "http://ngiss.t-online.de/cm1s/media/40e5d10666540db54a54bb2092a47faa39a52ec8.png", None, None, None, None, None, None, None),
        (None, "Bergblick.de", "45", "Bergblick", None, None, "Bergblick", "http://ngiss.t-online.de/cm1s/media/cc621620a4408b246b2b8e628f30b129c6bf08dc.png", "http://ngiss.t-online.de/cm1s/media/2f68a8b738d31415c99da911bea93a97020ee1f3.png", None, "BERGBLICK", None, None, None, None, None),
        (None, "BibelTV.de", "485", "Bibel TV", "BIBEL", "Bibel TV", "Bibel TV", "http://ngiss.t-online.de/cm1s/media/fc134f2137d5ab6b589f05da9b4d504ef7ef6510.png", "http://ngiss.t-online.de/cm1s/media/4754ecc68c5e078e80ac2d5435726b2a9b016b90.png", "http://live.tvspielfilm.de/static/images/channels/large/BIBEL.png", "BIBEL TV", "BIBELTV", None, None, None, None),
        (None, "BILD.de", "5077", "BILD", None, None, "Bild TV", "http://ngiss.t-online.de/cm1s/media/6e2b1f0a369f6dcd8d06773137228bc85ae5b4c6.png", "http://ngiss.t-online.de/cm1s/media/ccc0c6e49f79515cb678f5441e7befcb3e5255f5.png", None, "BILD TV", None, None, None, None, None),
        (None, "BonGusto.de", "117", "BonGusto", None, None, "Bon Gusto", "http://ngiss.t-online.de/cm1s/media/c1b8b637efa554081624dbcee2257dbe813a6ba0.png", "http://ngiss.t-online.de/cm1s/media/65ebe25329d441714dc70fa737e90c68c2a6e129.png", None, "BON GUSTO", None, None, None, None, None),
        (None, "BRFernsehen.de", "407", "BR Fernsehen Süd", "BR", "BR", "BR", "http://ngiss.t-online.de/cm1s/media/cb58c7fa22f3ab971a6344c01f058b1345f9f741.jpeg", "http://ngiss.t-online.de/cm1s/media/40d2ab4ade690ec7e4d965e586a62ca937ee091c.png", "http://live.tvspielfilm.de/static/images/channels/large/BR.png", "BAYERISCHES FERNSEHEN NORD", "BAYERISCHES FERNSEHEN SUD", "BR", "BR TV", None, None),
        (None, "CartoonNetwork.de", "4512", "Cartoon Network (Sky)", "C-NET", "Cartoon Network", "Cartoon Network", "http://ngiss.t-online.de/cm1s/media/62db037b6484ffd2e0c2aa3642c19958eb292c80.png", "http://ngiss.t-online.de/cm1s/media/f73ed871486bd026ffc3ff4cf5e5ac2eeaf6f746.png", "http://live.tvspielfilm.de/static/images/channels/large/C-NET.png", "CARTOON NETWORK", None, None, None, None, None),
        (None, "Channel21.de", "5176", "CHANNEL21", None, None, "Channel21", "http://ngiss.t-online.de/cm1s/media/97be4b435420b9d4bba4d6387415f6ec2a553a60.png", "http://ngiss.t-online.de/cm1s/media/eb86d7033816033536232cfa5a1c03c396b64d28.png", None, "CHANNEL 21", None, None, None, None, None),
        (None, "ComedyCentralVIVA.de", "50", "Comedy Central", "CC", "Comedy Central", "Comedy Central", "http://ngiss.t-online.de/cm1s/media/d53ac960c377cc6e7fba0946689a7cf881caa608.png", "http://ngiss.t-online.de/cm1s/media/766e5d3738b790d93690b9a6a40e65b99cb73d6b.png", "http://live.tvspielfilm.de/static/images/channels/large/CC.png", "COMEDY CENTRAL", "NICK/COMEDY CENTRAL1", None, None, None, None),
        (None, "CrimeInvestigation.de", "106", "Crime+Investigation", "CRIN", "CRIME + INVESTIGATION", "Crime + Investigation", "http://ngiss.t-online.de/cm1s/media/dfd75d6307871c1d4f40d5741b92c3d411835dec.png", "http://ngiss.t-online.de/cm1s/media/98c3430141aaf756c564aedafebb36d0258f34c1.png", "http://live.tvspielfilm.de/static/images/channels/large/CRIN.png", "CRIME INVESTIGATION", "CRIME & INVESTIGATION", "CRIME  INVESTIGATION", "CRIME+ INVESTIGATION", None, None),
        (None, "CuriosityChannel.de", "186", "Curiosity Channel", "SPTVW", "Spiegel TV Wissen", "Spiegel TV Wissen", "http://ngiss.t-online.de/cm1s/media/325486fcef8f3898f0012d7a89a3e3dccd2cb8de.png", "http://ngiss.t-online.de/cm1s/media/7502f4f2236a2916323f079e168237ffd7150a25.png", "http://live.tvspielfilm.de/static/images/channels/large/SPTVW.png", "SPIEGEL TV WISSEN", "SPIEGEL WISSEN", None, None, None, None),
        (None, "DasErste.de", "373", "Das Erste", "ARD", "Das Erste", "Das Erste", "http://ngiss.t-online.de/cm1s/media/cf416cc96a575e40e35f43c05d829efdb176bc35.png", "http://ngiss.t-online.de/cm1s/media/3711d16d0e3570276ebba175620385b5f4ff18f4.png", "http://live.tvspielfilm.de/static/images/channels/large/ARD.png", "ARD DAS ERSTE", "DAS ERSTE", "ARD", None, None, None),
        (None, "dazn1.de", "5507", "DAZN 1", "DAZN", "DAZN", "DAZN 1", "http://ngiss.t-online.de/cm1s/media/498bbbdd4dd1744448e9fb33777059d30e3ef6b0.jpeg", "http://ngiss.t-online.de/cm1s/media/7c93cbccfa99c23171441af6ba8f35cd22d9cf28.png", "http://live.tvspielfilm.de/static/images/channels/large/DAZN.png", None, None, None, None, None, None),
        (None, "dazn2.de", "5508", "DAZN 2", None, None, "DAZN 2", "http://ngiss.t-online.de/cm1s/media/7c972a4018118354837c15ea3774f7efbb5a1780.jpeg", "http://ngiss.t-online.de/cm1s/media/141a3d65b2f92f7e2a52c93d30a0a29f2184466d.png", None, None, None, None, None, None, None),
        (None, "DeLuxeMusic.de", "25", "DELUXE MUSIC", "DMC", "DELUXE MUSIC", "Deluxe Music", "http://ngiss.t-online.de/cm1s/media/0c7d8589ef1ecac504e6441bf09db1188f9d9a54.png", "http://ngiss.t-online.de/cm1s/media/d31840e010d6da58d1aeb2009b04f5a9924481c1.png", "http://live.tvspielfilm.de/static/images/channels/large/DMC.png", "DELUXE MUSIC", None, None, None, None, None),
        (None, "DeutschesMusikFernsehen.de", "5312", "Deutsches Musik Fernsehen", "DMF", "Deutsches Musik Fernsehen", "Deutsches Musik Fernsehen", "http://ngiss.t-online.de/cm1s/media/0f65355c1a6ab0c2c08627ade930c2a2aca9f7ad.png", "http://ngiss.t-online.de/cm1s/media/febc89b3d6ee8a59fce7915cc9ccc7b4448cfd3e.png", "http://live.tvspielfilm.de/static/images/channels/large/DMF.png", "DEUTSCHES MUSIK", "DEUTSCHES MUSIK FERNSEHEN", "EUTSCHES MUSIK FERNSEHEN", None, None, None),
        (None, "DiscoveryChannel.de", "468", "Discovery Channel (Sky)", "HDDIS", "Discovery HD", "Discovery Channel", "http://ngiss.t-online.de/cm1s/media/ea845e7451e73ccd87dbea800822c4dccbd11345.png", "http://ngiss.t-online.de/cm1s/media/6e522d9ae4b2a9a8f686281f7d3adff2d8862ee3.png", "http://live.tvspielfilm.de/static/images/channels/large/HDDIS.png", "DISCOVERY", "DISCOVERY CHANNEL", "DISCOVERY WORLD", None, None, None),
        (None, "disneychannel.de", "27", "Disney Channel", "DISNE", "Disney Channel", "Disney Channel", "http://ngiss.t-online.de/cm1s/media/43023439bd3b7a134d90116f72d8911dceeb7a85.png", "http://ngiss.t-online.de/cm1s/media/8ddb880c89e880c0a150c17e355138b0341ed6ee.png", "http://live.tvspielfilm.de/static/images/channels/large/DISNE.png", "DISNEY CHANNEL", "DISNEY CINEMAGIC", "DISNEY XD", None, None, None),
        (None, "DMax.de", "429", "DMAX", "DMAX", "DMAX", "DMAX", "http://ngiss.t-online.de/cm1s/media/ddf2946d5dc4e747b294fadeeb5552643688a6a4.png", "http://ngiss.t-online.de/cm1s/media/f47210c8539cdcb85e4c468f83a281f6daa66b58.png", "http://live.tvspielfilm.de/static/images/channels/large/DMAX.png", "DMAX", None, None, None, None, None),
        (None, "eSports1.de", "191", "eSPORTS1", None, None, "eSPORTS1", "http://ngiss.t-online.de/cm1s/media/c295c992a70344eb7a9ba0b2058f91818902f434.png", "http://ngiss.t-online.de/cm1s/media/6e4cee1ab1da1d86af73c1bfb533f11fe7711c5b.png", None, None, None, None, None, None, None),
        (None, "Eurosport1.de", "389", "Eurosport 1", "EURO", "Eurosport 1", "Eurosport 1", "http://ngiss.t-online.de/cm1s/media/78c2b996afeb3ce1579cf2b322ee15216020b0b6.png", "http://ngiss.t-online.de/cm1s/media/18f200745e93b6c9848237acaaa008ea9f520f94.png", "http://live.tvspielfilm.de/static/images/channels/large/EURO.png", "EUROSPORT 1", "ESPORTS", None, None, None, None),
        (None, "Eurosport2.de", "18", "Eurosport 2", "EURO2", "Eurosport 2", "Eurosport 2", "http://ngiss.t-online.de/cm1s/media/2e93193d3564e9ceba2faf1a89427e489b5d981a.png", "http://ngiss.t-online.de/cm1s/media/fbc41d77249de69bb35febcff1bb74dd87a3b031.png", "http://live.tvspielfilm.de/static/images/channels/large/EURO2.png", "EUROSPORT 2", None, None, None, None, None),
        (None, "GEO.de", "153", "GEO Television", None, None, "GEO Television", "http://ngiss.t-online.de/cm1s/media/9dd569bb4c1de835f21d29ac6fa9202c4d692a2e.png", "http://ngiss.t-online.de/cm1s/media/267643eb7bc861bb7e308a303f66e5301e848db7.png", None, "GEO TELEVISION", "GEO TV", None, None, None, None),
        (None, "Hamburg1.de", "244", "Hamburg 1", None, None, "HH1", "http://ngiss.t-online.de/cm1s/media/5847318b1dc2e8988fd51e45b5abdcae3b16ff95.png", "http://ngiss.t-online.de/cm1s/media/254cb8179b6bf0b87bf6e8907d184203dbca13b3.png", None, None, None, None, None, None, None),
        (None, "Heimatkanal.de", "661", "Heimatkanal", "HEIMA", "Heimatkanal", "Heimatkanal", "http://ngiss.t-online.de/cm1s/media/bde2d6cf0a6444e7c5d69dda485e41a4c7c19d00.png", "http://ngiss.t-online.de/cm1s/media/daabe8d88933d58ca50ef01e692058fe39759627.png", "http://live.tvspielfilm.de/static/images/channels/large/HEIMA.png", "HEIMAT KANAL", "HEIMATKANAL", None, None, None, None),
        (None, "HGTV.de", "3583", "HGTV", None, None, "HGTV", "http://ngiss.t-online.de/cm1s/media/fc0f32de5bfb782974da67e5fa6fc7c4ffcb2a64.png", "http://ngiss.t-online.de/cm1s/media/f1d655994f8af8a636f983c9d3fe1a862501766d.png", None, "HGTV", None, None, None, None, None),
        (None, "History.de", "162", "The HISTORY Channel", "HISHD", "History HD", "History Channel", "http://ngiss.t-online.de/cm1s/media/97239fbad4b1fc35897aab8a1c3371f94d71c3c5.png", "http://ngiss.t-online.de/cm1s/media/c991f75a9b93fb49233fe78cbcc37007d99e01ad.png", "http://live.tvspielfilm.de/static/images/channels/large/HISHD.png", "HISTORY", "HISTORY CHANNEL", None, None, None, None),
        (None, "HRFernsehen.de", "386", "hr-fernsehen", "HR", "HR", "hr-fernsehen", "http://ngiss.t-online.de/cm1s/media/a11fd9cb379e64e3c87a02d08004efe71bb4370d.png", "http://ngiss.t-online.de/cm1s/media/b11ecb6905afbf9f82d9cd8624c242013a78824e.png", "http://live.tvspielfilm.de/static/images/channels/large/HR.png", "HR FERNSEHEN", "HR-FERNSEHEN", None, None, None, None),
        (None, "HSE24.de", "451", "HSE", None, None, "HSE24", "http://ngiss.t-online.de/cm1s/media/968cb75741a60283e32c7872073b153e0599e346.png", "http://ngiss.t-online.de/cm1s/media/af654601ccb9e529f85c736e2c66e9fb96d62acc.png", None, "HSE 24 TV", "HSE", "HSE EXTRA", None, None, None),
        (None, "Jukebox.de", "132", "Jukebox (Sky)", "JUKE", "Jukebox", "Jukebox", "http://ngiss.t-online.de/cm1s/media/5b2bf4b5995f479d962a0e5154a7976d752b3ec4.png", "http://ngiss.t-online.de/cm1s/media/9735a7ac5cfcf3c56acd644069751c8c5b72bbe8.png", "http://live.tvspielfilm.de/static/images/channels/large/JUKE.png", "JUKEBOX", None, None, None, None, None),
        (None, "KabelEins.de", "405", "Kabel Eins", "K1", "kabel eins", "Kabel 1", "http://ngiss.t-online.de/cm1s/media/97cabed29d22f5726bc367c02f7f7860e7e95ea4.png", "http://ngiss.t-online.de/cm1s/media/e92cc62717350cd0378f1191c21a3512362c65a1.png", "http://live.tvspielfilm.de/static/images/channels/large/K1.png", "KABEL 1", "KABEL EINS", "KABEL 1 1080", None, None, None),
        (None, "KabelEinsClassic.de", "157", "Kabel Eins CLASSICS", "K1CLA", "kabel eins classics", "kabel eins classics", "http://ngiss.t-online.de/cm1s/media/a58e98653f4966262ca6d714b555f583cdd5870e.png", "http://ngiss.t-online.de/cm1s/media/3d6c4e11c8058b35f0726c1e25ab1b391a2ada75.png", "http://live.tvspielfilm.de/static/images/channels/large/K1CLA.png", "KABEL 1 CLASSICS", "KABEL EINS CLASSICS", None, None, None, None),
        (None, "KabelEinsDoku.de", "573", "Kabel Eins Doku", "K1DOKU", "kabel eins Doku", "Kabel Eins Doku", "http://ngiss.t-online.de/cm1s/media/6e13a0345c0d40adb0f718755c315dce6269af1d.png", "http://ngiss.t-online.de/cm1s/media/ca3279d86270655d49eb50a361e1dcb4564bf39e.png", "http://live.tvspielfilm.de/static/images/channels/large/K1DOKU.png", "KABEL 1 DOKU", "KABEL EINS DOKU", None, None, None, None),
        (None, "Kika.de", "387", "KiKA", "KIKA", "KiKA", "Kika", "http://ngiss.t-online.de/cm1s/media/2f0ff7b44c615c4de521878f52a67bc204e90ccc.png", "http://ngiss.t-online.de/cm1s/media/7d9a501ddc07382fcfdbb0c0797916ba4e78cacd.png", "http://live.tvspielfilm.de/static/images/channels/large/KIKA.png", "KIKA", None, None, None, None, None),
        (None, "Kinowelt.de", "137", "KinoweltTV", "KINOW", "KinoweltTV", "Kinowelt", "http://ngiss.t-online.de/cm1s/media/ebdbf39814820b3b2fa697c7c5f18c2d2d42bfde.png", "http://ngiss.t-online.de/cm1s/media/8f80fdd4f8fe6853800aeec106062fc2ee1d5ab4.png", "http://live.tvspielfilm.de/static/images/channels/large/KINOW.png", "KINOWELT TV", None, None, None, None, None),
        (None, "KTV.de", "487", "K-TV", "KTV", "K-TV", "K-TV", "http://ngiss.t-online.de/cm1s/media/f62d3893591005668f2e193cda40f65926db93db.png", "http://ngiss.t-online.de/cm1s/media/e942c7a5d723ecea30ee55121067d86cf541f262.png", "http://live.tvspielfilm.de/static/images/channels/large/KTV.png", "K-TV", "K TV", None, None, None, None),
        (None, "LustPur.de", "32", "Lust pur", None, None, "Lust Pur", "http://ngiss.t-online.de/cm1s/media/b7ebdc82026f8f0c8c630e31fb9de32df0cabf69.png", "http://ngiss.t-online.de/cm1s/media/35264aa89ecba0a3ceb4b0f6f4e0eae0eefb9fcf.png", None, None, None, None, None, None, None),
        (None, "MarcoPoloTV.de", "5295", "Marco Polo TV", None, None, "Marco Polo TV", "http://ngiss.t-online.de/cm1s/media/032e58edbf4dd69baa823381a928ffec7b36812e.png", "http://ngiss.t-online.de/cm1s/media/f8877cba3e440dc9d7d62e1bd51250b06fe2b03a.png", None, None, None, None, None, None, None),
        (None, "MDRS-Anhalt.de", "370", "MDR-Fernsehen Sachsen", "MDR", "MDR", "MDR Sachsen", "http://ngiss.t-online.de/cm1s/media/cbef55175586e7549bc32d052386620bdaa46ffc.jpeg", "http://ngiss.t-online.de/cm1s/media/8e11c0abde6c90a68507070c73b443401a24fcff.png", "http://live.tvspielfilm.de/static/images/channels/large/MDR.png", "MDR", "MDR FERNSEHEN ANHALT", "MDR FERNSEHEN SACHSEN ANHALT", "MDR TH", "MDR S-ANHALT", None),
        (None, "MotorVision.de", "604", "Motorvision+", "MOVTV", "Motorvision TV", "MotorVision", "http://ngiss.t-online.de/cm1s/media/c106fe8ef548c796be95ef4d6e17d7718e8f765e.png", "http://ngiss.t-online.de/cm1s/media/744220404bda665ff97622e9adc9969540e05895.png", "http://live.tvspielfilm.de/static/images/channels/large/MOVTV.png", "MOTORVISION", "MOTORVISION TV", None, None, None, None),
        (None, "MTVGermany.de", "28", "MTV", "MTV", "MTV", "MTV Germany", "http://ngiss.t-online.de/cm1s/media/168b11e1cd29dad018263863ebd1ba3085694b39.png", "http://ngiss.t-online.de/cm1s/media/95d8d4289c6a6056f67cac44eded24ad7b8cce8a.png", "http://live.tvspielfilm.de/static/images/channels/large/MTV.png", "MTV", None, None, None, None, None),
        (None, "MunchenTV.de", "241", "münchen.tv", None, None, "München TV", "http://ngiss.t-online.de/cm1s/media/e40a00b13deb139237015d3e9baff4da2a5cc203.png", "http://ngiss.t-online.de/cm1s/media/0c7f41025f6eb921088338aaca24116787652f0c.png", None, "MUENCHEN", "MÜNCHEN TV", None, None, None, None),
        (None, "N24Doku.de", "553", "N24 Doku", "N24DOKU", "N24 Doku", "N24 Doku", "http://ngiss.t-online.de/cm1s/media/72792fbb249037ecda95dc74746a3b328259584c.png", "http://ngiss.t-online.de/cm1s/media/bf4ce870d460dcdb3b1e573d58a14137a7d002ea.png", "http://live.tvspielfilm.de/static/images/channels/large/N24DOKU.png", "N24 DOCU", "N24 DOKU", "N24", None, None, None),
        (None, "NatGeoHD.de", "35", "National Geographic", "N-GHD", "Nat Geo HD", "National Geographic", "http://ngiss.t-online.de/cm1s/media/300ee96526ee22e83abc8cd72778715c6d8be000.png", "http://ngiss.t-online.de/cm1s/media/c9d4a2fb172069fc67d4170738cdbbc225f079f6.png", "http://live.tvspielfilm.de/static/images/channels/large/N-GHD.png", "NAT GEO", "NATIONAL GEOGRAPHIC", None, None, None, None),
        (None, "NatGeoWild.de", "569", "National Geographic Wild", "N-GW", "NAT GEO WILD", "Nat Geo Wild", "http://ngiss.t-online.de/cm1s/media/825ae85bec16d0c4c593df6419d05971fa13017b.png", "http://ngiss.t-online.de/cm1s/media/deec95134d0baec0f4030cb9c96a1f7348419c30.png", "http://live.tvspielfilm.de/static/images/channels/large/N-GW.png", "NAT GEO WILD", None, None, None, None, None),
        (None, "NDRFernsehen.de", "377", "NDR Fernsehen Niedersachsen", "N3", "NDR", "NDR FS MV", "http://ngiss.t-online.de/cm1s/media/0c990ed7599bb3786b9abe9575b2ab5cbe39698d.jpeg", "http://ngiss.t-online.de/cm1s/media/d72e120a384a97f269eb891ad135fb4d115decbb.png", "http://live.tvspielfilm.de/static/images/channels/large/N3.png", "NDR", "NDR FERNSEHEN", None, None, None, None),
        (None, "NickJr.de", "221", "Nick Jr.", "NICKJ", "Nick Jr.", "Nick Junior", "http://ngiss.t-online.de/cm1s/media/fd4fdfd9465ebbc2a23b6e484de08f530d6415a2.png", "http://ngiss.t-online.de/cm1s/media/cfa3bf59d761bb21a108955f7dd919d04ef20734.png", "http://live.tvspielfilm.de/static/images/channels/large/NICKJ.png", "JUNIOR", "NICK JR", "NICK JUNIOR", "SKY JUNIOR", None, None),
        (None, "Nicktoons.de", "4405", "Nicktoons (Sky)", "NICKT", "Nicktoons", "NickToons", "http://ngiss.t-online.de/cm1s/media/cfbcb5d88a89ecd5137071f97a5d25e7ab3a4d03.png", "http://ngiss.t-online.de/cm1s/media/9361033a288cb7f1f525416eef433f1d47c38abf.png", "http://live.tvspielfilm.de/static/images/channels/large/NICKT.png", "NICKTOONS", None, None, None, None, None),
        (None, "ntv.de", "376", "n-tv", "NTV", "n-tv", "n-tv", "http://ngiss.t-online.de/cm1s/media/4aeedcd569e01554c2ead254a2e846855f8ba4a0.png", "http://ngiss.t-online.de/cm1s/media/1c3073dd69376d57149afdb1791c2576724000f2.png", "http://live.tvspielfilm.de/static/images/channels/large/NTV.png", "NTV", "N-TV", "N TV", None, None, None),
        (None, "One.de", "402", "ONE", "FES", "ONE", "One", "http://ngiss.t-online.de/cm1s/media/5388fcfe85425017a8b8ef3c9b6083c6e4a05ebf.png", "http://ngiss.t-online.de/cm1s/media/70b3ed315768d8799f8577aad1003e4b2758b197.png", "http://live.tvspielfilm.de/static/images/channels/large/FES.png", "ONE", "ONEBY", None, None, None, None),
        (None, "phoenix.de", "371", "phoenix", "PHOEN", "PHOENIX", "PHOENIX", "http://ngiss.t-online.de/cm1s/media/3363e853ea8c2bd2568dc233d3006f205b86096b.png", "http://ngiss.t-online.de/cm1s/media/0630170ba6401342025bf2ca1b1ed337e653bed5.png", "http://live.tvspielfilm.de/static/images/channels/large/PHOEN.png", "PHOENIX", None, None, None, None, None),
        (None, "ProSieben.de", "374", "ProSieben", "PRO7", "ProSieben", "ProSieben", "http://ngiss.t-online.de/cm1s/media/67c3154ef4906af6324dc75cdd2ec4b8f32ba77d.png", "http://ngiss.t-online.de/cm1s/media/a7f56de9d6b8af8708bda4a48349ab6a3f713ecd.png", "http://live.tvspielfilm.de/static/images/channels/large/PRO7.png", "PRO 7", "PROSIEBEN", "PRO7", None, None, None),
        (None, "ProSiebenFun.de", "259", "ProSieben FUN", "PRO7F", "ProSieben Fun", "Pro7 Fun", "http://ngiss.t-online.de/cm1s/media/40e41e7fc04d7c6f355e4cb818abc0f1fa9221a0.png", "http://ngiss.t-online.de/cm1s/media/1f0e9026087e023f7464640bcbe4eaed6cce4055.png", "http://live.tvspielfilm.de/static/images/channels/large/PRO7F.png", "PRO 7 FUN", "PRO7 FUN", "PROSIEBEN FUN", None, None, None),
        (None, "ProSiebenMaxx.de", "396", "ProSieben MAXX", "PRO7M", "ProSieben MAXX", "ProSieben Maxx", "http://ngiss.t-online.de/cm1s/media/39803d8155ac67b6eb5ebc6fc9ee0f776bda9078.png", "http://ngiss.t-online.de/cm1s/media/8bbd8b6505244eadf79acc39552459c44c052ffa.png", "http://live.tvspielfilm.de/static/images/channels/large/PRO7M.png", "PRO7 MAXX", "PRO 7 MAXX", "PROSIEBEN MAXX", None, None, None),
        (None, "QVC.de", "446", "QVC", None, None, "QVC", "http://ngiss.t-online.de/cm1s/media/fd01d35d5c28a955c3e7e62a65d1018feb3b8317.png", "http://ngiss.t-online.de/cm1s/media/d985b7be308774435b4e824e87857be6d01626a0.png", None, "QVC", None, None, None, None, None),
        (None, "RadioBremen.de", "368", "Radio Bremen TV", None, None, "Radio Bremen TV", "http://ngiss.t-online.de/cm1s/media/241dbee528b6f4faa42cebf930862c86e3da7a2d.jpeg", "http://ngiss.t-online.de/cm1s/media/cd648267d785ddb46756676b9d0b5ee806a60a7d.png", None, None, None, None, None, None, None),
        (None, "rbbBerlin.de", "384", "rbb fernsehen Berlin", None, None, "rbb Berlin", "http://ngiss.t-online.de/cm1s/media/9b1dec3a1c1cb52d5af57a5a58f6fa0f285cc7c8.jpeg", "http://ngiss.t-online.de/cm1s/media/3c5a2a45fa454d43b49eb1a696cafd0a4eeb1c86.png", None, "RBB", "RBB BERLIN", None, None, None, None),
        (None, "RheinNeckarFernsehen.de", "246", "RNF", None, None, "RNF", "http://ngiss.t-online.de/cm1s/media/757141d8c04ba40355376f94d46e7e92cc066c11.png", "http://ngiss.t-online.de/cm1s/media/c1dd9de99f0eabc4c3f8efa1a6a7c15631783360.png", None, None, None, None, None, None, None),
        (None, "RiC.de", "5329", "RiC", None, None, "RiC", "http://ngiss.t-online.de/cm1s/media/32b3fa60cefdac40612320c661a468518f709b98.png", "http://ngiss.t-online.de/cm1s/media/d3793d2e6881bb5ba207356a5ac262a4c96264eb.png", None, None, None, None, None, None, None),
        (None, "Romance.de", "658", "Romance TV (Sky)", "ROM", "Romance TV", "Romance TV", "http://ngiss.t-online.de/cm1s/media/a7090918dd814d59d3aff662fd317b7dd2a176c7.png", "http://ngiss.t-online.de/cm1s/media/26147f4735983c4f20ad71c01ba95f25b1a7ccc7.png", "http://live.tvspielfilm.de/static/images/channels/large/ROM.png", "ROMANCE TV", None, None, None, None, None),
        (None, "RTL.de", "404", "RTL", "RTL", "RTL", "RTL", "http://ngiss.t-online.de/cm1s/media/9837608c7cfa66c854354b00e53992f6861bcd1a.png", "http://ngiss.t-online.de/cm1s/media/3f21af88cf184a45ff4c54be37053ddd678e2456.png", "http://live.tvspielfilm.de/static/images/channels/large/RTL.png", "RTL", None, None, None, None, None),
        (None, "RTL2.de", "382", "RTLZWEI", "RTL2", "RTL II", "RTL II", "http://ngiss.t-online.de/cm1s/media/bcfa273955d4de5c524ab6a632793d4e0ca5d340.png", "http://ngiss.t-online.de/cm1s/media/c2f437c77a06daffbcaa14f5caed1b301abda6b7.png", "http://live.tvspielfilm.de/static/images/channels/large/RTL2.png", "RTL 2", "RTL ZWEI", None, None, None, None),
        (None, "RTLCrime.de", "216", "RTL Crime", "RTL-C", "RTL Crime", "RTL Crime", "http://ngiss.t-online.de/cm1s/media/5c3418953e0ecfc4b18f07e3dc3c455ec8614387.png", "http://ngiss.t-online.de/cm1s/media/fda6a6827c4ba695a264061adc0a8813eb83afa7.png", "http://live.tvspielfilm.de/static/images/channels/large/RTL-C.png", "RTL CRIME", None, None, None, None, None),
        (None, "RTLLiving.de", "227", "RTL Living", "RTL-L", "RTL Living", "RTL Living", "http://ngiss.t-online.de/cm1s/media/6f0521746c669921ebea9f610235046858d9dfdd.png", "http://ngiss.t-online.de/cm1s/media/df96334494725e0766bf3a22ac6ae3ea88611adf.png", "http://live.tvspielfilm.de/static/images/channels/large/RTL-L.png", "RTL LIVING", None, None, None, None, None),
        (None, "RTLNitro.de", "395", "NITRO", "RTL-N", "NITRO", "RTL Nitro", "http://ngiss.t-online.de/cm1s/media/d39e08b7e07394cf436285fb47ed36c0037b89c6.png", "http://ngiss.t-online.de/cm1s/media/3e55a412683a498ae7e19077ea81b564bb1b271b.png", "http://live.tvspielfilm.de/static/images/channels/large/RTL-N.png", "NITRO", "RTL NITRO", None, None, None, None),
        (None, "RTLPassion.de", "209", "RTL Passion", "PASS", "RTL Passion", "RTL Passion", "http://ngiss.t-online.de/cm1s/media/1e9ac8f92edf2760a1208f37d0c1bb7702eb849e.png", "http://ngiss.t-online.de/cm1s/media/f723199cfa53cb06b833be3a91bc36f301fbafc8.png", "http://live.tvspielfilm.de/static/images/channels/large/PASS.png", "RTL PASSION", None, None, None, None, None),
        (None, "RTLup.de", "542", "RTLup", "RTLPL", "RTLplus", "RTLup", "http://ngiss.t-online.de/cm1s/media/7c2f4696435b5416266cd09b356420953d5ff280.png", "http://ngiss.t-online.de/cm1s/media/f0eab07df247d9f64761c2d9f6e12d244d5ed0b5.png", "http://live.tvspielfilm.de/static/images/channels/large/RTLPL.png", "RTL UP", "RTLUP", None, None, None, None),
        (None, "Sat1.de", "381", "SAT.1", "SAT1", "SAT.1", "Sat 1", "http://ngiss.t-online.de/cm1s/media/d36b5ed6e8b046be225671f62b42f6362c55ee22.png", "http://ngiss.t-online.de/cm1s/media/efd5a2c8992cd87d3fcc83b5b2399d12971bf89f.png", "http://live.tvspielfilm.de/static/images/channels/large/SAT1.png", "SAT 1", None, None, None, None, None),
        (None, "Sat1Comedy.de", "224", "SAT.1 emotions", "SAT1E", "SAT.1 emotions", "Sat.1 emotions", "http://ngiss.t-online.de/cm1s/media/611aafacc609a226b45e4b6a9f5ec25e6063207d.png", "http://ngiss.t-online.de/cm1s/media/fb8cf407e719419c47b394d4307cb3e7aa16c4ae.png", "http://live.tvspielfilm.de/static/images/channels/large/SAT1E.png", "SAT 1 EMOTIONS", None, None, None, None, None),
        (None, "Sat1Gold.de", "338", "SAT.1 GOLD", "SAT1G", "SAT.1 Gold", "Sat1 Gold HD", "http://ngiss.t-online.de/cm1s/media/50e21d837d6ca501ef59c832f139c269ea173bf5.png", "http://ngiss.t-online.de/cm1s/media/c4df738dfcdc4307911328c1368b717428f234d8.png", "http://live.tvspielfilm.de/static/images/channels/large/SAT1G.png", "SAT.1 GOLD", "SAT 1 GOLD", None, None, None, None),
        (None, "SciFi.de", "465", "SYFY (Sky)", "SCIFI", "Syfy", "Syfy", "http://ngiss.t-online.de/cm1s/media/0fe285bc64ebc70a42b03567e044e37ddf9247ee.png", "http://ngiss.t-online.de/cm1s/media/ea9846917902c635cd3c5b239bd2f0c5d23c0c98.png", "http://live.tvspielfilm.de/static/images/channels/large/SCIFI.png", "SYFY", None, None, None, None, None),
        (None, "ServusHD.de", "39", "ServusTV", "SERVU", "ServusTV", "Servus TV HD", "http://ngiss.t-online.de/cm1s/media/add45c3af659a41db5b91c2bb98827ab1e09acc9.png", "http://ngiss.t-online.de/cm1s/media/7705473aad92b6a66fbd0d0f845ba5a884d69989.png", "http://live.tvspielfilm.de/static/images/channels/large/SERVU.png", "SERVUS TV", None, None, None, None, None),
        (None, "Sixx.de", "380", "sixx", "SIXX", "sixx", "SIXX", "http://ngiss.t-online.de/cm1s/media/de47028468ad1df49de852883dc42addad5825c1.png", "http://ngiss.t-online.de/cm1s/media/2dc9daa2cdf850169e75d472bd42362f60a0cd7f.png", "http://live.tvspielfilm.de/static/images/channels/large/SIXX.png", "SIXX", None, None, None, None, None),
        (None, "Sky1.de", "576", "Sky One", "SKY1", "Sky One", "Sky 1", "http://ngiss.t-online.de/cm1s/media/0686f6f18a8950c0938a98c6dd19d416228752b7.png", "http://ngiss.t-online.de/cm1s/media/1a2ed987272b88d35770eae839376b8807836a84.png", "http://live.tvspielfilm.de/static/images/channels/large/SKY1.png", "SKY 1", None, None, None, None, None),
        (None, "SkyAction.de", "40", "Sky Cinema Action", "SKY-A", "Sky Action", "Sky Action", "http://ngiss.t-online.de/cm1s/media/72b47f9ddfae42dea1fb594d4ce65282ac1887af.png", "http://ngiss.t-online.de/cm1s/media/62de0add95c271dede017fb50d22f6de51ffa34d.png", "http://live.tvspielfilm.de/static/images/channels/large/SKY-A.png", "SKY ACTION", "SKY CINEMA ACTION", None, None, None, None),
        (None, "SkyAtlanticHD.de", "264", "Sky Atlantic", "SKYAT", "Sky Atlantic HD", "Sky Atlantic", "http://ngiss.t-online.de/cm1s/media/67a6531b3ef8e686027b424f95e676182ff35791.png", "http://ngiss.t-online.de/cm1s/media/e9fd1abc76e3b402cf5ae4f65bf6798741cd214e.png", "http://live.tvspielfilm.de/static/images/channels/large/SKYAT.png", "SKY ARTS", "SKYLANTIC", "SKY ATLANTIC", None, None, None),
        (None, "SkyBundesliga1.de", "206", "Sky Sport Bundesliga 1", "BULI", "Sky Sport Bundesliga", "Sky Sport Bundesliga 1", "http://ngiss.t-online.de/cm1s/media/315f4e1d7ae0ed6a576cc85574c6e195f2820925.png", "http://ngiss.t-online.de/cm1s/media/4200a7071dfb0095510d7ed65682da53ba833eec.png", "http://live.tvspielfilm.de/static/images/channels/large/BULI.png", "SKY BUNDESLIGA1", "SKY BUNDESLIGA 1", None, None, None, None),
        (None, "SkyBundesliga10.de", "5557", "Sky Sport Bundesliga 10", None, None, "Sky Sport Bundesliga 10", "http://ngiss.t-online.de/cm1s/media/d00d089e311ba581066027cff70935778efaf201.png", "http://ngiss.t-online.de/cm1s/media/083d140c6df8ca522b605c2c9ca9fb24a92455f3.png", None, "SKY BUNDESLIGA 10", None, None, None, None, None),
        (None, "SkyBundesliga2.de", "211", "Sky Sport Bundesliga 2", None, None, "Sky Sport Bundesliga 2", "http://ngiss.t-online.de/cm1s/media/54fdfb49171a1da7210ccf22d8f8af24934365e1.png", "http://ngiss.t-online.de/cm1s/media/157acf7ce820d15b32b3b032403a32fb65958ac2.png", None, "SKY BUNDESLIGA 2", None, None, None, None, None),
        (None, "SkyBundesliga3.de", "199", "Sky Sport Bundesliga 3", None, None, "Sky Sport Bundesliga 3", "http://ngiss.t-online.de/cm1s/media/b7604a3db1310d4a4fb83fffb15debe55d41dbf7.png", "http://ngiss.t-online.de/cm1s/media/059d08de74e6183963d844496ffa1d96b7e264ef.png", None, "SKY BUNDESLIGA 3", None, None, None, None, None),
        (None, "SkyBundesliga4.de", "232", "Sky Sport Bundesliga 4", None, None, "Sky Sport Bundesliga 4", "http://ngiss.t-online.de/cm1s/media/ab1f8d87c8f74b510387c81c0a89aa004006ee60.png", "http://ngiss.t-online.de/cm1s/media/1896c9e512a830512a50aead481612e623c7fc40.png", None, "SKY BUNDESLIGA 4", None, None, None, None, None),
        (None, "SkyBundesliga5.de", "234", "Sky Sport Bundesliga 5", None, None, "Sky Sport Bundesliga 5", "http://ngiss.t-online.de/cm1s/media/9fbf9f911b60bb7c0bbfceaf6b0506cadf63cc02.png", "http://ngiss.t-online.de/cm1s/media/e1b0693d92286bae1481f232ff087a4f0cd3b7e1.png", None, "SKY BUNDESLIGA 5", None, None, None, None, None),
        (None, "SkyBundesliga6.de", "231", "Sky Sport Bundesliga 6", None, None, "Sky Sport Bundesliga 6", "http://ngiss.t-online.de/cm1s/media/1f8dc21b9fce64499d61956f407ab5a72cb78ed0.png", "http://ngiss.t-online.de/cm1s/media/18b38a657b0333c91513befb793a06e06d5e6f58.png", None, "SKY BUNDESLIGA 6", None, None, None, None, None),
        (None, "SkyBundesliga7.de", "258", "Sky Sport Bundesliga 7", None, None, "Sky Sport Bundesliga 7", "http://ngiss.t-online.de/cm1s/media/ec53727b223a2c6b129c78e2b06c7f45cce4659a.png", "http://ngiss.t-online.de/cm1s/media/25af99e420b22dc62986815785d2eac63c9d132b.png", None, "SKY BUNDESLIGA 7", None, None, None, None, None),
        (None, "SkyBundesliga8.de", "219", "Sky Sport Bundesliga 8", None, None, "Sky Sport Bundesliga 8", "http://ngiss.t-online.de/cm1s/media/d997f9be46160f7c3db14cbdc3cf2b48fc6eb274.png", "http://ngiss.t-online.de/cm1s/media/b23310b91343dae0296d313b692b52dbbdec8d69.png", None, "SKY BUNDESLIGA 8", None, None, None, None, None),
        (None, "SkyBundesliga9.de", "237", "Sky Sport Bundesliga 9", None, None, "Sky Sport Bundesliga 9", "http://ngiss.t-online.de/cm1s/media/e48399d331a672785f16f1011054a01cd52413df.png", "http://ngiss.t-online.de/cm1s/media/282435adc67782bce8ea32e0b92173f6d76baf4f.png", None, "SKY BUNDESLIGA 9", None, None, None, None, None),
        (None, "SkyCinemaClassics.de", "200", "Sky Cinema Classics", "SKY-N", "Sky Cinema Classics", "Sky Cinema Classics", "http://ngiss.t-online.de/cm1s/media/611c7452027ed8309b22df4396bb359a6c7ac9d6.png", "http://ngiss.t-online.de/cm1s/media/14c205585d3d1c5728d0575c661dc0d12c340ef1.png", "http://live.tvspielfilm.de/static/images/channels/large/SKY-N.png", "SKY CINEMA CLASSICS", "SKY CINEMA NOSTALGIE", "SKY CLASSICS", "SKY NOSTALGIE", "SKY SERIEN & SHOWS", "SKY SERIEN&SHOWS"),
        (None, "SkyCinemaFamily.de", "572", "Sky Cinema Family", "SKY-F", "Sky Family", "Sky Cinema Family", "http://ngiss.t-online.de/cm1s/media/97652da8fb13e92531ed3eacd719ab0952f494b1.png", "http://ngiss.t-online.de/cm1s/media/4af8c51b0aae80d28cb887cd75fe15508aea515f.png", "http://live.tvspielfilm.de/static/images/channels/large/SKY-F.png", "SKY CINEMA FAMILY", "SKY FAMILY", None, None, None, None),
        (None, "SkyCinemaFun.de", "235", "Sky Cinema Fun", "SKY-C", "Sky Cinema Fun", "Sky Cinema Fun", "http://ngiss.t-online.de/cm1s/media/f6a7bf52afe312c829e02a1471b7781129647220.png", "http://ngiss.t-online.de/cm1s/media/b49bd59ff13cb015a5ab9243bf102d6b3d1cc4be.png", "http://live.tvspielfilm.de/static/images/channels/large/SKY-C.png", "SKY CINEMA FUN", "SKY FUN", None, None, None, None),
        (None, "SkyCinemaPlus1.de", "195", "Sky Cinema Premieren", "CIN", "Sky Cinema Premieren", "Sky Cinema +1", "http://ngiss.t-online.de/cm1s/media/c28c2033bbba5d0423a10e93a5fe985ac9645f29.png", "http://ngiss.t-online.de/cm1s/media/0b253961f1ed86531231b7ebef4856fe2393998c.png", "http://live.tvspielfilm.de/static/images/channels/large/CIN.png", "SKY CINEMA 1", "SKY CINEMA +1", "SKY CINEMA PREMIEREN", "SKY CINEMA PREMIERE", None, None),
        (None, "SkyCinemaPlus24.de", "202", "Sky Cinema Premieren +24", "CIN24", "Sky Cinema Premieren +24", "Sky Cinema+24", "http://ngiss.t-online.de/cm1s/media/f2af068e6cfa5e574aa0a3e629d3a932c6ea74fb.png", "http://ngiss.t-online.de/cm1s/media/5371a1404566488319991aef236525c5cdd96fd0.png", "http://live.tvspielfilm.de/static/images/channels/large/CIN24.png", "SKY CINEMA 24", "SKY CINEMA PREMIEREN 24", "SKY PREMIEREN 24", "SKY CINEMA +24", "SKY CINEMA PREMIEREN +24", None),
        (None, "SkyCinemaSpecial.de", "3844", "Sky Cinema Special", "SKYCS", "Sky Cinema Special HD", "Sky Cinema Best Of 2019 HD", "http://ngiss.t-online.de/cm1s/media/b4935d33ecfe29e85ae1786abc650159acbd9ec2.png", "http://ngiss.t-online.de/cm1s/media/2c4c6b314f2e5280c36b01434468d73c7d8c6ab7.png", "http://live.tvspielfilm.de/static/images/channels/large/SKYCS.png", "SKY CINEMA SPECIAL", "SKY SPECIAL", "SKY BEST OF", "SKY CINEMA BEST", "SKY CINEMA BEST OF", None),
        (None, "SkyCinemaThriller.de", "4356", "Sky Cinema Thriller", "SKYTH", "Sky Cinema Thriller", "Sky Cinema Thriller", "http://ngiss.t-online.de/cm1s/media/4df156eaa910ee8c40d2a74cba5ed628d22f850a.png", "http://ngiss.t-online.de/cm1s/media/e72acc4e943682e5c0fc1bc320a6fbe2b9675fd0.png", "http://live.tvspielfilm.de/static/images/channels/large/SKYTH.png", "SKY CINEMA EMOTION", "SKY CINEMA THRILLER", "SKY THRILLER", None, None, None),
        (None, "SkyCrime.de", "4924", "Sky Crime", None, None, "Sky Crime", "http://ngiss.t-online.de/cm1s/media/4f03dd50f05666fc0dd66e4e39cfd9b11d564f14.png", "http://ngiss.t-online.de/cm1s/media/55f7af6e6da0e5fe88c98d17969ec3567cde00c6.png", None, "SKY CINEMA CRIME", "SKY CRIME", None, None, None, None),
        (None, "SkyDocumentaries.de", "5143", "Sky Documentaries", None, None, "Sky Documentaries", "http://ngiss.t-online.de/cm1s/media/88edcb4b636b84c5a45280e43fc2d09f091b7e7e.png", "http://ngiss.t-online.de/cm1s/media/d678db56c8ea3648fe89d02a8b017a8b9a7d9f06.png", None, "SKY DOCUMENTARIES", None, None, None, None, None),
        (None, "SkyKrimi.de", "201", "Sky Krimi", "SKY-K", "Sky Krimi", "Sky Krimi", "http://ngiss.t-online.de/cm1s/media/084a614a9133ae1b17cc942bbe0d81a87710030b.png", "http://ngiss.t-online.de/cm1s/media/2092514be53beb3a7d0b25a95db91ed27c707c8b.png", "http://live.tvspielfilm.de/static/images/channels/large/SKY-K.png", "SKY KRIMI", None, None, None, None, None),
        (None, "SkyNature.de", "5142", "Sky Nature", None, None, "Sky Nature", "http://ngiss.t-online.de/cm1s/media/3fc118ed29130cea4498adb9fce21ad7fa2595c0.png", "http://ngiss.t-online.de/cm1s/media/6ed382f8ee9fb14dd678d78dbe4d4d8c2f9ff0c5.png", None, "SKY NATURE", None, None, None, None, None),
        (None, "SkyReplay.de", "3756", "Sky Replay", None, None, "Sky Replay", "http://ngiss.t-online.de/cm1s/media/0427e3d448898a5424abccc805e235bbeded6876.png", "http://ngiss.t-online.de/cm1s/media/5727b8cc057a36b525abafb23b46d02bb24fed70.png", None, "FOX", "SKY REPLAY", None, None, None, None),
        (None, "SkyShowcase.de", "5577", "Sky Showcase", None, None, "Sky Showcase", "http://ngiss.t-online.de/cm1s/media/344837d83882d97841fdc7e8d7556a05bb4a4411.png", "http://ngiss.t-online.de/cm1s/media/09629b5939190f0df366f958f199d6d499b2c4bd.png", None, None, None, None, None, None, None),
        (None, "SkySport1.de", "192", "Sky Sport 1", None, None, "Sky Sport 1", "http://ngiss.t-online.de/cm1s/media/bfca3bcb13981de2a46b970f3167110e0f3c5a83.png", "http://ngiss.t-online.de/cm1s/media/de52c5d48628b03453d6c09ff0d625ccd9123329.png", "http://live.tvspielfilm.de/static/images/channels/large/HDSPO.png", "SKY SPORT 1", None, None, None, None, None),
        (None, "SkySport10.de", "5554", "Sky Sport 10", None, None, "Sky Sport 10", "http://ngiss.t-online.de/cm1s/media/25751836767f9282d88d99e61c38a1529b0616d3.png", "http://ngiss.t-online.de/cm1s/media/402fc1d16a4b7072aa3ec0a6382178a6a874afd6.png", None, "SKY SPORT 10", None, None, None, None, None),
        (None, "SkySport2.de", "212", "Sky Sport 2", None, None, "Sky Sport 2", "http://ngiss.t-online.de/cm1s/media/c330c871a2f15660efbf06c917fc6af8606874c7.png", "http://ngiss.t-online.de/cm1s/media/a81a83173f2b76a9167bb872d535645d12ff16c5.png", "http://live.tvspielfilm.de/static/images/channels/large/SHD2.png", "SKY SPORT 2", None, None, None, None, None),
        (None, "SkySport3.de", "189", "Sky Sport 3", None, None, "Sky Sport 3", "http://ngiss.t-online.de/cm1s/media/f3093734389bd620327880348d7974ba38d4c4d3.png", "http://ngiss.t-online.de/cm1s/media/1206e226d77c64a66c18676d2a4995ac0d4f528e.png", None, "SKY SPORT 3", None, None, None, None, None),
        (None, "SkySport4.de", "111", "Sky Sport 4", None, None, "Sky Sport 4", "http://ngiss.t-online.de/cm1s/media/c6a8dbde2b6d4afa5961586d6317f0cc86ddc6e9.png", "http://ngiss.t-online.de/cm1s/media/33e321e0ea47007d4fe5840b462f324425c04b77.png", None, "SKY SPORT 4", None, None, None, None, None),
        (None, "SkySport5.de", "114", "Sky Sport 5", None, None, "Sky Sport 5", "http://ngiss.t-online.de/cm1s/media/cda082d3267802e1bd0721e6a64850b2920ac427.png", "http://ngiss.t-online.de/cm1s/media/174bc4e879e6dfe8da2da79a20d1cd12a2e64a11.png", None, "SKY SPORT 5", None, None, None, None, None),
        (None, "SkySport6.de", "113", "Sky Sport 6", None, None, "Sky Sport 6", "http://ngiss.t-online.de/cm1s/media/acc2e098dc86b8c85a1bbfa5f6311b5978603e1c.png", "http://ngiss.t-online.de/cm1s/media/dccedc966ee1e760137bbf38f34d86f0793ab7ed.png", None, "SKY SPORT 6", None, None, None, None, None),
        (None, "SkySport7.de", "127", "Sky Sport 7", None, None, "Sky Sport 7", "http://ngiss.t-online.de/cm1s/media/3957d066cf0f424aabd67e0d677737ff0c2b524c.png", "http://ngiss.t-online.de/cm1s/media/2f260de91a03cc79f32ad816be1aae5e424fc523.png", None, "SKY SPORT 7", None, None, None, None, None),
        (None, "SkySport8.de", "261", "Sky Sport 8", None, None, "Sky Sport 8", "http://ngiss.t-online.de/cm1s/media/27bc8c5ac71da92955eb4952145b305d6d1813d5.png", "http://ngiss.t-online.de/cm1s/media/b355966e88194e9b72e2879cece8735834a1b45a.png", None, "SKY SPORT 8", None, None, None, None, None),
        (None, "SkySport9.de", "187", "Sky Sport 9", None, None, "Sky Sport 9", "http://ngiss.t-online.de/cm1s/media/2b19683849d2f29ba98a944a4489a09625603b14.png", "http://ngiss.t-online.de/cm1s/media/68a5a9c16947d1423678be66c7223fc5f4e5d037.png", None, "SKY SPORT 9", None, None, None, None, None),
        (None, "SkySportBundesliga.de", "42", "Sky Sport Bundesliga", None, None, "Sky Sport Bundesliga", "http://ngiss.t-online.de/cm1s/media/e05bdb7a982d1d570cf99d19ad357d5572e477eb.png", "http://ngiss.t-online.de/cm1s/media/cf8a1da7411cef9e690ad178cedbd9dbe13ebdbd.png", None, None, None, None, None, None, None),
        (None, "SkySportF1.de", "4889", "Sky Sport F1", "SKYF1", "Sky Sport F1", "Sky Sport F1", "http://ngiss.t-online.de/cm1s/media/5e262f2be1a0530c07327d65e867d74b524fac03.png", "http://ngiss.t-online.de/cm1s/media/67d611a4e282db524f86d9424d2ce0921bdca5a3.png", "http://live.tvspielfilm.de/static/images/channels/large/SKYF1.png", "SKY SPORT F1", None, None, None, None, None),
        (None, "SkySportGolf.de", "5558", "Sky Sport Golf", None, None, "Sky Sport Golf", "http://ngiss.t-online.de/cm1s/media/4522d64c5b2b9fd8ed24d3cd9e03d918dc32037d.png", "http://ngiss.t-online.de/cm1s/media/20375ea6aa459f3e75ff52ef8dd025257f91c453.png", None, "SKY SPORT GOLF", "S. SPORT GOLF", None, None, None, None),
        (None, "SkySportMix.de", "5556", "Sky Sport Mix", None, None, "Sky Sport Mix HD", "http://ngiss.t-online.de/cm1s/media/ed2e5bdbaddbfbb84f40d2980fd9bf4022a5a1b9.png", "http://ngiss.t-online.de/cm1s/media/5494143bb12d192a5c0b69b5f93c2d3368e00fbd.png", None, "SKY SPORT MIX", None, None, None, None, None),
        (None, "SkySportNewsHD.de", "190", "Sky Sport News", "SNHD", "Sky Sport News", "Sky Sport News", "http://ngiss.t-online.de/cm1s/media/2498751ec7f984ac0d80376e61d8322492d69b83.png", "http://ngiss.t-online.de/cm1s/media/73b37ddf8cadce6a5c4a1ebdf70a526c2ae93719.png", "http://live.tvspielfilm.de/static/images/channels/large/SNHD.png", "SKY SPORT NEWS", "S. SPORT NEWS", None, None, None, None),
        (None, "SkySportPremierLeague.de", "5555", "Sky Sport Premier League", None, None, "Sky Sport Premier League", "http://ngiss.t-online.de/cm1s/media/7cf51fbd8edfb9a32257339ecb7ad0f8eee8b989.png", "http://ngiss.t-online.de/cm1s/media/398c412f21c4d52385bffd49f852338d56b43808.png", None, "SKY SPORT PREMIERE LEAGUE", "SKY SPORT PREMIER LEAGUE", "S. SPORT PREMIER LEAGUE", None, None, None),
        (None, "SkySportTennis.de", "198", "Sky Sport Tennis", None, None, "Sky Sport Tennis", "http://ngiss.t-online.de/cm1s/media/2b8c1e691bf3f12b2ca1d01fe233ebf4871d8808.png", "http://ngiss.t-online.de/cm1s/media/e69c367167782ff684da93d889c980eec8ea0bfd.png", None, "SKY SPORT TENNIS", None, None, None, None, None),
        (None, "SkySportTopEvent.de", "31", "Sky Sport Top Event", None, None, "Sky Sport Top Event", "http://ngiss.t-online.de/cm1s/media/577040e2d47ce20ce71f0985bd447e2f328542fd.png", "http://ngiss.t-online.de/cm1s/media/8693b13e8355d376c9b2c53e515e7f85abe659d9.png", None, "SKY SPORT TOP EVENT", None, None, None, None, None),
        (None, "SonnenKlar.de", "486", "sonnenklar.TV", "SKLAR", "Sonnenklar.TV", "Sonnenklar", "http://ngiss.t-online.de/cm1s/media/cb7dc216efdc0daa6b956f55f60793f9449793bc.png", "http://ngiss.t-online.de/cm1s/media/14573aebde590f886d975d5193a26dc6065c0683.png", "http://live.tvspielfilm.de/static/images/channels/large/SKLAR.png", "SONNENKLAR TV", None, None, None, None, None),
        (None, "SpiegelGeschichte.de", "4406", "Spiegel Geschichte", "SP-GE", "Spiegel Geschichte", "Spiegel Geschichte HD", "http://ngiss.t-online.de/cm1s/media/4a3ca85ec049f0a5209e87cc49a151eeaccfc84c.jpeg", "http://ngiss.t-online.de/cm1s/media/cb6141ae4226647544a9af4b6d69e41d557fe894.png", "http://live.tvspielfilm.de/static/images/channels/large/SP-GE.png", "SPIEGEL GESCHICHTE", None, None, None, None, None),
        (None, "SPORT1plus.de", "44", "SPORT1+", None, None, "Sport1+", "http://ngiss.t-online.de/cm1s/media/af9a42b6042b440dcbe2d2b0eec4a8ddf5c271af.png", "http://ngiss.t-online.de/cm1s/media/074034f464715db15c5859b60b36558cac35a5e3.png", None, None, None, None, None, None, None),
        (None, "sportdigital.de", "194", "SPORTDIGITAL FUSSBALL", "SPO-D", "sportdigital Fussball", "Sportdigital", "http://ngiss.t-online.de/cm1s/media/58639959eb7241ee5cc8dbf96122c1f73ec809a9.png", "http://ngiss.t-online.de/cm1s/media/36207a17b0a5760b3977dcf130e53ce30f09c594.png", "http://live.tvspielfilm.de/static/images/channels/large/SPO-D.png", "SPORT DIGITAL", "SPORTDIGITAL FUSSBALL", "SPORTDIGITALL FUSSBALL", None, None, None),
        (None, "SRFernsehen.de", "379", "SR Fernsehen", "SF1", "SRF 1", "SR Fernsehen", "http://ngiss.t-online.de/cm1s/media/f8a9f5bb4d09df24243b3d94d237552e57160395.jpeg", "http://ngiss.t-online.de/cm1s/media/784cfb3e89c660ecf9f02bae301f40f875996af9.png", "http://live.tvspielfilm.de/static/images/channels/large/SF1.png", "SR", "SR FERNSEHEN", "SRF EINS", "SRF EINS DE", "SRF 1", None),
        (None, "SuperRTL.de", "403", "Super RTL", "SUPER", "SUPER RTL", "Super RTL", "http://ngiss.t-online.de/cm1s/media/d424d9dd46e4aadf15c9b290f9566022e1f751e3.png", "http://ngiss.t-online.de/cm1s/media/d83d20be89d5f6899d8885b944b109928f7a3171.png", "http://live.tvspielfilm.de/static/images/channels/large/SUPER.png", "SUPER RTL", None, None, None, None, None),
        (None, "SWRFernsehen-rp.de", "393", "SWR Fernsehen RP", None, None, "SWR Fernsehen RP", "http://ngiss.t-online.de/cm1s/media/90a1d123b1106d7115bb84be54b9f113ecb591d0.jpeg", "http://ngiss.t-online.de/cm1s/media/033802069c0c3086585d215e0592501669f15f1c.png", None, None, None, None, None, None, None),
        (None, "SWRFernsehen.de", "398", "SWR Fernsehen BW", "SWR", "SWR/SR", "Südwest Fernsehen", "http://ngiss.t-online.de/cm1s/media/cee24651f02bb81fcccde46a4d4ef4e9175ba525.jpeg", "http://ngiss.t-online.de/cm1s/media/033802069c0c3086585d215e0592501669f15f1c.png", "http://live.tvspielfilm.de/static/images/channels/large/SWR.png", "SWR", "SWR FERNSEHEN", "SWR DE", None, None, None),
        (None, "tagesschau24.de", "400", "tagesschau24", "TAG24", "tagesschau24", "tagesschau24", "http://ngiss.t-online.de/cm1s/media/efb9c4d31b9a35b7c239bbc1ad32379ba8638671.png", "http://ngiss.t-online.de/cm1s/media/2d0ef79c908ad450db7ddc28eaf7076a02e162af.png", "http://live.tvspielfilm.de/static/images/channels/large/TAG24.png", "TAGESSCHAU 24", "TAGESSCHAU24", None, None, None, None),
        (None, "Tele5.de", "48", "TELE 5", "TELE5", "Tele 5", "Tele 5", "http://ngiss.t-online.de/cm1s/media/32a48373344696c10ba67188d40b84276a5ffbb8.jpeg", "http://ngiss.t-online.de/cm1s/media/05452ad179e25678e50434da167e2f3ede2a9f60.png", "http://live.tvspielfilm.de/static/images/channels/large/TELE5.png", "TELE 5", "TELE 5 TV", None, None, None, None),
        (None, "TLC.de", "383", "TLC", "TLC", "TLC", "TLC", "http://ngiss.t-online.de/cm1s/media/b586ac90cc3f2a1b5b684c3040248b3f8a4b50ea.png", "http://ngiss.t-online.de/cm1s/media/bd43973022bc8b5e4e44ecaf07cbeaaca3943fd6.png", "http://live.tvspielfilm.de/static/images/channels/large/TLC.png", "TLC", None, None, None, None, None),
        (None, "TOGGOplus.de", "601", "TOGGO plus", "TOGGO", "TOGGO plus", "TOGGOplus", "http://ngiss.t-online.de/cm1s/media/744f1eae71634557d366ad03a96d557dd4d8cc50.png", "http://ngiss.t-online.de/cm1s/media/35d704a6beeecc53be277ba5e9342ddca6df5e0a.png", "http://live.tvspielfilm.de/static/images/channels/large/TOGGO.png", "TOGGO PLUS", "TOGGO", None, None, None, None),
        (None, "Universal.de", "185", "Universal TV", "UNIVE", "Universal Channel HD", "Universal Channel", "http://ngiss.t-online.de/cm1s/media/7f48afa094b2c72438c121e0554924a52dbd928b.png", "http://ngiss.t-online.de/cm1s/media/1994bd733a17fbcd32d1d78dc43b28c362776f5b.png", "http://live.tvspielfilm.de/static/images/channels/large/UNIVE.png", "UNIVERSAL CHANNEL", "UNIVERSAL TV", None, None, None, None),
        (None, "Vox.de", "385", "VOX", "VOX", "VOX", "VOX", "http://ngiss.t-online.de/cm1s/media/ab1b4db17f18456ab5fef3b39180c2f0fac69833.png", "http://ngiss.t-online.de/cm1s/media/0e5b4d41d518a068a0bef830d64f848b84ac39d1.png", "http://live.tvspielfilm.de/static/images/channels/large/VOX.png", "VOX", None, None, None, None, None),
        (None, "VOXup.de", "3930", "VOXup", "VOXUP", "VOXup", "VOXup", "http://ngiss.t-online.de/cm1s/media/343f563d2dfffc0ef1ef4c10fe83bc88b5dfdad3.png", "http://ngiss.t-online.de/cm1s/media/7475b5f5fce6df60756901f94904c42d2675c6d9.png", "http://live.tvspielfilm.de/static/images/channels/large/VOXUP.png", "VOXUP", "VOX UP", None, None, None, None),
        (None, "WarnerTVComedy.de", "181", "Warner TV Comedy", "TNT-C", "TNT Comedy", "Warner Comedy", "http://ngiss.t-online.de/cm1s/media/86f2a216f921da95f55efe5e9b9b29a8f5a88d5d.png", "http://ngiss.t-online.de/cm1s/media/793f9b574904a15207169109b57f7b52979e9d14.png", "http://live.tvspielfilm.de/static/images/channels/large/TNT-C.png", "TNT COMEDY", "WARNER COMEDY", "WARNER TV COMEDY", "WBTV COMEDY", None, None),
        (None, "WarnerTVFilm.de", "184", "Warner TV Film", "TNT-F", "TNT Film", "Warner Film", "http://ngiss.t-online.de/cm1s/media/3548467648337ce97c4f4403b74e834be29e2f41.png", "http://ngiss.t-online.de/cm1s/media/a4a10078c8d5e31bb59574f9fb4df3ae7d6f975b.png", "http://live.tvspielfilm.de/static/images/channels/large/TNT-F.png", "TNT FILM", "WARNER FILM", "WARNER TV FILM", "TNT FILM TCM", "WBTV FILM", None),
        (None, "WarnerTVSerie.de", "53", "Warner TV Serie", "TNT-S", "TNT Serie", "Warner Serie", "http://ngiss.t-online.de/cm1s/media/c192e34369025dd8d010c4a1dc40dafd08d2501b.png", "http://ngiss.t-online.de/cm1s/media/ac63870aec09e2977583b416e2547620552e6c4d.png", "http://live.tvspielfilm.de/static/images/channels/large/TNT-S.png", "TNT SERIE", "WARNER SERIE", "WARNER TV SERIE", "WBTV SERIE", None, None),
        (None, "WDRFernsehen.de", "397", "WDR Fernsehen Köln", "WDR", "WDR", "WDR Köln", "http://ngiss.t-online.de/cm1s/media/4602315f65a534d5b9d342e7b265fa1c52f483b2.jpeg", "http://ngiss.t-online.de/cm1s/media/8784546120200060bc84357fcafd0994d648ee40.png", "http://live.tvspielfilm.de/static/images/channels/large/WDR.png", "WDR", "WDR DE", None, None, None, None),
        (None, "WedoMovies.de", "5399", "wedo movies", None, None, "wedo movies", "http://ngiss.t-online.de/cm1s/media/8234e568500ac4b9119fb880af589772d9f0d75d.png", "http://ngiss.t-online.de/cm1s/media/f45a2a145e9188a561e5cbf4e6e77a48e2388fd3.png", None, None, None, None, None, None, None),
        (None, "WELT.de", "375", "WELT", "WELT", "WELT", "Welt", "http://ngiss.t-online.de/cm1s/media/27b5768478a2c8dbae1accd6fce7180eff6267cf.png", "http://ngiss.t-online.de/cm1s/media/949412402d4f2ba8cf1b63ebed3223b6c652765d.png", "http://live.tvspielfilm.de/static/images/channels/large/WELT.png", "WELT", "WELT/ N24", "WELT/N24", None, None, None),
        (None, "WeltDerWunder.de", "60", "Welt der Wunder", "WDWTV", "Welt der Wunder TV", "Welt der Wunder", "http://ngiss.t-online.de/cm1s/media/b34ca6367edd117b07dcfc59f1b12c61b2d1fe6d.png", "http://ngiss.t-online.de/cm1s/media/629f72770f72b4f816843f063e0281d9b3d355d9.png", "http://live.tvspielfilm.de/static/images/channels/large/WDWTV.png", "WELTR WUNDER", "WELTR WUNDER TV", "WELT DER WUNDER TV", None, None, None),
        (None, "Wetterfernsehen.de", "571", "wetter.com TV", None, None, "wetter.com TV", "http://ngiss.t-online.de/cm1s/media/7dd1aeba5f4bfdf43c3e2c87db051cf7635a9e85.png", "http://ngiss.t-online.de/cm1s/media/18ebe2c3ee90c1060da7a5498d2f7e846321271b.png", None, None, None, None, None, None, None),
        (None, "ZDF.de", "408", "ZDF", "ZDF", "ZDF", "ZDF", "http://ngiss.t-online.de/cm1s/media/e19130e25f23d70df7f85807c6ddc1c8d62109f5.png", "http://ngiss.t-online.de/cm1s/media/35d71e6d09f3551cb4053da8487b3028cf9339cd.png", "http://live.tvspielfilm.de/static/images/channels/large/ZDF.png", "ZDF", None, None, None, None, None),
        (None, "ZDFinfo.de", "378", "ZDFinfo", "ZINFO", "ZDFinfo", "ZDFinfokanal", "http://ngiss.t-online.de/cm1s/media/1aeb69ec2c60a45a57bc0c01fd6c36b6dbf377e7.png", "http://ngiss.t-online.de/cm1s/media/60641d1e04421f17dd4369382a389b0d7599b736.png", "http://live.tvspielfilm.de/static/images/channels/large/ZINFO.png", "ZDF INFO", None, None, None, None, None),
        (None, "ZDFneo.de", "391", "ZDFneo", "2NEO", "ZDFneo", "ZDF neo", "http://ngiss.t-online.de/cm1s/media/cb898bc1d4f4291a994851ae22ae93b40467181c.png", "http://ngiss.t-online.de/cm1s/media/9f4bcfe2464370144428eeac56b55f1cfb061109.png", "http://live.tvspielfilm.de/static/images/channels/large/2NEO.png", "ZDF NEO", None, None, None, None, None),
        (None, "6eren.dk", None, None, None, None, None, None, None, None, "6EREN", None, None, None, None, None),
        (None, "Puls8.ch", None, None, None, None, None, None, None, None, "ACHT", None, None, None, None, None),
        (None, "AandE.de", None, None, None, None, None, None, None, None, "A&E", None, None, None, None, None),
        (None, "allgauTV.de", None, None, None, None, None, None, None, None, "ALLGAU", "ALLGAU TV", None, None, None, None),
        (None, "AstroTV.de", None, None, None, None, None, None, None, None, "ASTRO TV", None, None, None, None, None),
        (None, "ATV2.at", None, None, None, None, None, None, None, None, "ATV 2", None, None, None, None, None),
        (None, "a.tv.de", None, None, None, None, None, None, None, None, "AUGSBURG", "AUGSBURG TV", None, None, None, None),
        (None, "BadenTV.de", None, None, None, None, None, None, None, None, "BADEN TV", None, None, None, None, None),
        (None, "Boomerang.de", None, None, None, None, None, None, None, None, "BOOMERANG", None, None, None, None, None),
        (None, "CANAL9.dk", None, None, None, None, None, None, None, None, "CANAL 9", None, None, None, None, None),
        (None, "ChemnitzTV.de", None, None, None, None, None, None, None, None, "CHEMNITZ FERNSEHEN", None, None, None, None, None),
        (None, "#dabeiTV.de", None, None, None, None, None, None, None, None, "DABEITV", None, None, None, None, None),
        (None, "DAZN10.de", None, None, None, None, None, None, None, None, "DAZN 10", None, None, None, None, None),
        (None, "DAZN11.de", None, None, None, None, None, None, None, None, "DAZN 11", None, None, None, None, None),
        (None, "DAZN12.de", None, None, None, None, None, None, None, None, "DAZN 12", None, None, None, None, None),
        (None, "DAZN13.de", None, None, None, None, None, None, None, None, "DAZN 13", None, None, None, None, None),
        (None, "DAZN14.de", None, None, None, None, None, None, None, None, "DAZN 14", None, None, None, None, None),
        (None, "DAZN15.de", None, None, None, None, None, None, None, None, "DAZN 15", None, None, None, None, None),
        (None, "DAZN16.de", None, None, None, None, None, None, None, None, "DAZN 16", None, None, None, None, None),
        (None, "DAZN17.de", None, None, None, None, None, None, None, None, "DAZN 17", None, None, None, None, None),
        (None, "DAZN18.de", None, None, None, None, None, None, None, None, "DAZN 18", None, None, None, None, None),
        (None, "DAZN3.de", None, None, None, None, None, None, None, None, "DAZN 3", None, None, None, None, None),
        (None, "DAZN4.de", None, None, None, None, None, None, None, None, "DAZN 4", None, None, None, None, None),
        (None, "DAZN5.de", None, None, None, None, None, None, None, None, "DAZN 5", None, None, None, None, None),
        (None, "DAZN6.de", None, None, None, None, None, None, None, None, "DAZN 6", None, None, None, None, None),
        (None, "DAZN7.de", None, None, None, None, None, None, None, None, "DAZN 7", None, None, None, None, None),
        (None, "DAZN9.de", None, None, None, None, None, None, None, None, "DAZN 9", None, None, None, None, None),
        (None, "Der Aktionär TV", None, None, None, None, None, None, None, None, "DER AKTIONÄR TV", "DER AKTION R TV", None, None, None, None),
        (None, "DisneyJunior.de", None, None, None, None, None, None, None, None, "DISNEY JUNIOR", None, None, None, None, None),
        (None, "dk4.dk", None, None, None, None, None, None, None, None, "DK4", None, None, None, None, None),
        (None, "DR1.dk", None, None, None, None, None, None, None, None, "DR1", None, None, None, None, None),
        (None, "DR2.dk", None, None, None, None, None, None, None, None, "DR2", None, None, None, None, None),
        (None, "DRRamaSjang.dk", None, None, None, None, None, None, None, None, "DR RAMASJANG", None, None, None, None, None),
        (None, "EEntertainment.de", None, None, None, None, None, None, None, "http://live.tvspielfilm.de/static/images/channels/large/E!.png", "E!", "E! ENTERTAINMENT", "E! ENTERTAINEMENT", "E! ENTERTAIN", None, None),
        (None, "EdgeSport.de", None, None, None, None, None, None, None, None, "EDGE SPORT", None, None, None, None, None),
        (None, "EuronewsDE.nws", None, None, None, None, None, None, None, None, "EURONEWS", "EURONEWSUTSCH", None, None, None, None),
        (None, "FC BAYERN.TV LIVE", None, None, None, None, None, None, None, None, "FC BAYERN", "FC BAYERN TV", None, None, None, None),
        (None, "FixFoxi.de", None, None, "FFTV", "Fix & Foxi", None, None, None, "http://live.tvspielfilm.de/static/images/channels/large/FFTV.png", "FIX&FOXI", "FIX & FOXI", None, None, None, None),
        (None, "FolxTV.de", None, None, None, None, None, None, None, None, "FOLX", "FOLX TV", None, None, None, None),
        (None, "FrankenTV.de", None, None, None, None, None, None, None, None, "FRANKEN FERNSEHEN", "FRANKEN PLUS", None, None, None, None),
        (None, "GoldstarTV.de", None, None, None, None, None, None, None, None, "GOLDSTAR", None, None, None, None, None),
        (None, "Kanal4.dk", None, None, None, None, None, None, None, None, "KANAL 4", None, None, None, None, None),
        (None, "Kanal5.dk", None, None, None, None, None, None, None, None, "KANAL 5", None, None, None, None, None),
        (None, "Nickelodeon.de", None, None, "NICK", "nick", None, None, None, "http://live.tvspielfilm.de/static/images/channels/large/NICK.png", "NICKELODEON", "NICK KIDS", None, None, None, None),
        (None, "NRWision", None, None, None, None, None, None, None, None, "NRWISION", None, None, None, None, None),
        (None, "oe24.TV", None, None, None, None, None, None, None, None, "OE24.TV", None, None, None, None, None),
        (None, "OneMusicTelevision.de", None, None, None, None, None, None, None, None, "ONE MUSIC", None, None, None, None, None),
        (None, "ORF1.at", None, None, "ORF1", "ORF 1", None, None, None, "http://live.tvspielfilm.de/static/images/channels/large/ORF1.png", "ORF1", "ORF 1", None, None, None, None),
        (None, "ORF2.at", None, None, "ORF2", "ORF 2", None, None, None, "http://live.tvspielfilm.de/static/images/channels/large/ORF2.png", "ORF 2", None, None, None, None, None),
        (None, "ORFSport.at", None, None, None, None, None, None, None, None, "ORF SPORT", None, None, None, None, None),
        (None, "QVCPlus.de", None, None, None, None, None, None, None, None, "QVC 2", "QVC ZWEI", None, None, None, None),
        (None, "Oberbayern.de", None, None, None, None, None, None, None, None, "RFO", None, None, None, None, None),
        (None, "RNF.de", None, None, None, None, None, None, None, None, "RNF", None, None, None, None, None),
        (None, "SachsenEins.de", None, None, None, None, None, None, None, None, "SACHSENEINS", None, None, None, None, None),
        (None, "SachsenFernsehen-Dresden.de", None, None, None, None, None, None, None, None, "SACHSEN FERNSEHEN", None, None, None, None, None),
        (None, "SchlagerDeluxe.de", None, None, None, None, None, None, None, None, "SCHLAGERLUXE", None, None, None, None, None),
        (None, "Silverline.de", None, None, "SILVE", "Silverline", None, None, None, "http://live.tvspielfilm.de/static/images/channels/large/SILVE.png", "SILVERLINE", None, None, None, None, None),
        (None, "SkyComedy.de", None, None, None, None, None, None, None, None, "SKY CINEMA COMEDY", "SKY COMEDY", None, None, None, None),
        (None, "SkyCinemaHits.de", None, None, None, None, None, None, None, None, "SKY CINEMA HITS", None, None, None, None, None),
        (None, "SkyPopcornSelect1.de", None, None, None, None, None, None, None, None, "SKY POPCORN SELECT 1", None, None, None, None, None),
        (None, "SkySport11.de", None, None, None, None, None, None, None, None, "SKY SPORT 11", None, None, None, None, None),
        (None, "AXNWhite.de", None, None, "SONY", "Sony Channel", None, None, None, "http://live.tvspielfilm.de/static/images/channels/large/SONY.png", "SONY CHANNEL", None, None, None, None, None),
        (None, "Sport1HD.de", None, None, None, None, None, None, None, None, "SPORT 1", "SPORT1", None, None, None, None),
        (None, "TVAOstbayern.de", None, None, None, None, None, None, None, None, "TVA OSTBAYERN", None, None, None, None, None),
        (None, "tvingolstadt.de", None, None, None, None, None, None, None, None, "TV INGOLSTADT", None, None, None, None, None),
        (None, "tvmainfranken.de", None, None, None, None, None, None, None, None, "TV MAINFRANKEN", None, None, None, None, None),
        (None, "tvo.de", None, None, None, None, None, None, None, None, "TV OBERFRANKEN", None, None, None, None, None),
        (None, "Waidwerk.de", None, None, None, None, None, None, None, None, "WAIDWERK", "WAIDWERK TV", None, None, None, None)
    ]
    for row in epg:
        cur.execute('INSERT INTO epgs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', row)
    con.commit()
    con.close()
    ifile = open('/home/pyodide/sql.db','rb')
    bytes_list = bytearray(ifile.read())
    my_bytes = io.BytesIO(bytes_list)
    db_file = File.new([Uint8Array.new(my_bytes.getvalue())], "vxplayer.db")
    window.App.writeFileToFS(db_file)
    console.log('[DB][Created]')


def reLoad():
    global htmlInput
    body = document.querySelector('body')
    lines = ''
    lines += htmlInput['s1']
    lines += htmlInput['s2']
    lines += htmlInput['main']
    body.innerHTML = lines
    menuBuilder()


def load():
    global htmlInput
    body = document.querySelector('body')
    lines = ''
    lines += htmlInput['s1']
    lines += htmlInput['s2']
    lines += htmlInput['main']
    body.innerHTML += lines

    db_buffer = window.App.getDB()
    if db_buffer == '0':
        createDB()
        time.sleep(5)
        db_buffer = window.App.getDB()
    if not db_buffer == '0':
        console.log('db buffer')
        raw_bytes = db_buffer.to_bytes()
        with open('database.db', "wb") as file_handle:
            file_handle.write(raw_bytes)
            file_handle.close()
        global con
        con = sqlite3.connect('database.db')
        unicode = str
        con.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
        con.text_factory = lambda x: unicode(x, errors='ignore')
        menuBuilder()
        checkLists()
    pass


def writeListToDB(listName, channels):
    global con
    cur = con.cursor()
    if not (test := cur.execute('SELECT * FROM lists WHERE type="VAVOO"').fetchone()):
        cur.execute('INSERT INTO lists VALUES (NULL,"VAVOO","Vavoo",NULL,NULL,NULL,NULL)')
        con.commit()
        test = cur.execute('SELECT * FROM lists WHERE type="VAVOO"').fetchone()
    lid = test['id']
    cur.execute('DELETE FROM channels WHERE lid="' + str(lid) + '"')
    con.commit()
    for c in channels:
        group = str(c['group'])
        logo = ''
        name = re.sub('( (AUSTRIA|AT|HEVC|RAW|SD|HD|FHD|UHD|H265|GERMANY|DEUTSCHLAND|1080|DE|S-ANHALT|SACHSEN|MATCH TIME)| \\|\\w+)|( \\(BACKUP\\))|\\(BACKUP\\)|( \\([\\w ]+\\))|\\([\\d+]\\)', '', c['name'].encode('ascii', 'ignore').decode('ascii'))
        tname = c['name'].encode('ascii', 'ignore').decode('ascii')
        tid = ''
        url = str(c['url'])
        if str(c['group']) == 'Germany':
            if (test := cur.execute('SELECT * FROM epgs WHERE name="' + name + '" OR name1="' + name + '" OR name2="' + name + '" OR name3="' + name + '" OR name4="' + name + '" OR name5="' + name + '"').fetchone()):
                if not test['rid'] == '' and not test['rid'] == None: tid = test['rid']
                if not test['display'] == '' and not test['display'] == None: name = test['display']
                if not test['ml'] == '' and not test['ml'] == None: logo = test['ml']
        cur.execute('INSERT INTO channels VALUES(NULL,"' + str(lid) + '","' + str(name) + '","' + str(group) + '","' + str(url) + '","' + str(logo) + '","' + str(tname) + '","' + str(tid) + '")')
    cur.execute('UPDATE lists SET last="' + str(int(time.time())) + '" WHERE type="VAVOO"')
    con.commit()
    saveDB()
    htmlBuilder(lid)




async def getGroups():
    global wsig
    if not wsig:
        sig = await getSig()
        wsig = sig

    _headers={"user-agent":"WATCHED/1.8.3 (android)", "accept": "application/json", "content-type": "application/json; charset=utf-8", "cookie": "lng=", "watched-sig": wsig}
    _data={"adult": True,"cursor": 0,"sort": "name"}
    response = await pyfetch(
        url="https://www.oha.to/oha-tv-index/directory.watched",
        method="POST",
        headers=_headers,
        body=json.dumps(_data)
    )
    if response.ok:
        r = await response.json()
        groups = json.loads(re.sub('\'', '"', str(r.get("features").get("filter")[0].get("values"))))
        if groups:
            return groups
    return None


async def getEpg():
    global con
    cur = con.cursor()
    epg_channels = []
    epg_ids = {}
    today = datetime.today()
    day_to_start = datetime(today.year, today.month, today.day, hour=00, minute=00, second=1)
    dts = day_to_start
    dts += timedelta(days=1)
    dtg = dts.strftime("%Y-%m-%d")
    day_to_grab = day_to_start.strftime("%Y-%m-%d")

    async def _get(tid, day):
        _url = 'https://live.tvspielfilm.de/static/broadcast/list/{}/{}'.format(tid, day)
        _header = {'Host': 'live.tvspielfilm.de',
                  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
                  'Accept-Encoding': 'gzip, deflate, br',
                  'Connection': 'keep-alive',
                  'Upgrade-Insecure-Requests': '1'}
        response = await pyfetch(
            _url
        )
        if response.ok:
            r = await response.json()
            return { 'tid': str(tid), 'values': r }
        return {}


    tasks = []
    for row in cur.execute('SELECT * FROM epgs ORDER BY id'):
        if not row['tid'] == None and not row['tid'] == '':
            epg_channels.append(str(row['tid']))
            epg_ids[str(row['tid'])] = str(row['rid'])

    for epg in epg_channels:
        task = asyncio.ensure_future(_get(epg, day_to_grab))
        tasks.append(task)
        task = asyncio.ensure_future(_get(epg, dtg))
        tasks.append(task)

    response = await asyncio.gather(*tasks)
    cur.execute('DELETE FROM epg')
    con.commit()
    for res in response:
        console.log(str(res))
        if 'tid' in res:
            rid = epg_ids[str(res['tid'])]
            for item in res['values']:
                if 'text' in item: desc = b64encode(str(item['text']).encode('utf-8'))
                else: desc = ''
                if 'episodeTitle' in item: title = b64encode(str(item['episodeTitle']).encode('utf-8'))
                else: title = ''
                end = str(item['timeend'])
                start = str(item['timestart'])
                lang = 'DE'
                cur.execute('INSERT INTO epg VALUES (NULL,"' + str(rid) + '","' + str(start) + '","' + str(end) + '","' + str(title) + '","' + str(desc) + '","' + str(lang) + '")')
    con.commit()
    saveDB()


async def getVavoo():
    global wsig, channels, tasks
    channels = []
    tasks = []

    async def _getchannels(group, cursor=0):
        global channels, wsig, tasks
        if not wsig:
            sig = await getSig()
            wsig = sig
        _headers={"user-agent":"WATCHED/1.8.3 (android)", "accept": "application/json", "content-type": "application/json; charset=utf-8", "cookie": "lng=", "watched-sig": wsig}
        _data={"adult": True,"cursor": cursor,"filter": {"group": group},"sort": "name"}
        response = await pyfetch(
            url="https://www.oha.to/oha-tv-index/directory.watched",
            method="POST",
            headers=_headers,
            body=json.dumps(_data)
        )
        if response.ok:
            r = await response.json()
            nextCursor = r.get("nextCursor")
            items = json.loads(re.sub('\'', '"', str(r.get("items"))))
            if nextCursor:
                task = asyncio.ensure_future(_getchannels(group, nextCursor))
                tasks.append(task)
            for item in items:
                channels.append(json.loads(re.sub('\'', '"', str(item))))
    if not wsig:
        sig = await getSig()
        wsig = sig
    groups = await getGroups()
    if groups:
        for group in groups:
            task = asyncio.ensure_future(_getchannels(group))
            tasks.append(task)
        await asyncio.gather(*tasks)
        writeListToDB('VAVOO', channels)


async def getSig():
    xlist=[
        "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"]
    try:
        response = await pyfetch(
            url="https://www.rokkr.net/api/box/ping",
            method="POST",
            headers={"Content-Type": "application/json; charset=UTF-8", "User-Agent": "Rokkr/1.8.3 (android)", "Accept": "application/json", "Content-Length": "2408", "Accept-Encoding": "gzip", "Cookie": "lng=en"},
            body=json.dumps({"x": random.choice(xlist)})
        )
        if response.ok:
            data = await response.json()
            sig = None
            if data.get('signed'):
                sig = data['signed']
            elif data.get('data', {}).get('signed'):
                sig = data['data']['signed']
            elif data.get('response', {}).get('signed'):
                sig = data['response']['signed']
            if sig:
                return sig
    except:
        return


if __name__ == '__main__':
    #console.log(window.App)
    #window.App.request('POST', 'https://www.rokkr.net/api/box/ping', '{"body":{"x": "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"}, "headers":[["Content-Type", "application/json; charset=UTF-8"],["User-Agent", "Rokkr/1.8.3 (android)"], ["Accept", "application/json"], ["Content-Length", "2408"], ["Accept-Encoding", "gzip"], ["Cookie", "lng=en"]]}', create_proxy(ttestt))
    document.body.focus()
    createDB()
    load()
    #asyncio.ensure_future(main())
    #console.log(sig)
