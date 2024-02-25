import sqlite3, os, json, sys, js, asyncio, re, time, pyscript, io, glob, random
import xml.etree.ElementTree as ET
from base64 import b64encode, b64decode
from pyscript import document, when, display, window
from pyodide.http import pyfetch, open_url
from pyodide.ffi import create_proxy
from datetime import datetime, timedelta
from js import alert, prompt, localStorage, Hls, FileReader, console, Uint8Array, File
from . import sql

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
            if row['logo'] == None or row['logo'] == '': logo = "no.png"
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
            epgOutput[str(rid)]['html'] += head %(title, str(datetime.fromtimestamp(int(test['start'])).strftime("%H:%M")), str(datetime.fromtimestamp(int(test['end'])).strftime("%H:%M")), desc)
            if (test := cur.execute('SELECT * FROM epg WHERE cid="'+str(rid)+'" AND start > "'+str(int(time.time()))+'" ORDER BY start').fetchone()):
                epgOutput[str(rid)]['start'] = int(test['start'])
                title = re.sub('b\'', '\'', str(b64decode(re.sub('b\'', '\'', test['title'])))).encode('ascii', 'ignore').decode('ascii')
                desc = re.sub('b\'', '\'', str(b64decode(re.sub('b\'', '\'', test['desc'])))).encode('ascii', 'ignore').decode('ascii')
                epgOutput[str(rid)]['html'] += head %(title, str(datetime.fromtimestamp(int(test['start'])).strftime("%H:%M")), str(datetime.fromtimestamp(int(test['end'])).strftime("%H:%M")), desc)
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
    epg = sql.epg
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
        if 'tid' in res:
            rid = epg_ids[str(res['tid'])]
            for item in res['values']:
                if 'text' in item: desc = str(item['text']).encode('utf-8')
                else: desc = ''
                if 'title' in item: title = str(item['title']).encode('utf-8')
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

