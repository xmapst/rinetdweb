#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author : lijunye
# @File : webserver.py
# @Time : 2019/1/10
# @Uptime : 
# @Version : 0.1
# @Features : 
# @Desc : rinted端口转发 WEB界面操作
"""

import web
import os
import time
import commands
import fileinput
import subprocess 
import shlex

render = web.template.render('templates/')
rinstate, rinetd_bin = commands.getstatusoutput('which rinetd')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONF = "conf/rinetd.conf"
PID = """ps -elf |grep rinetd|grep -v grep |awk '{print $4}'"""

if rinstate != 0:
    print("rinetd is not find")
    os._exit()

urls = (
    '/', 'Index',
    '/add', 'Add',
    '/del', 'Del',
    '/op(.*)', 'Operate'
    )
 
app = web.application(urls, globals())

def getConf():
    i = 0
    result = {}
    with open( CONF, 'r') as fobj:
        lines = fobj.readlines()
    for line in lines:
        line = line.strip('\n')
        result[i] = line
        i += 1
        print line

    k = ['SocIP', 'SocPort', 'DesIP', 'DesPort']
    for line in result.keys():
        v = str(result[line]).split()
        result[line] = dict(zip(k, v))
    return result

def rinetd_state():
    pid = commands.getoutput(PID)
    if pid == "":
        return "Rinetd已停止"
    else:
        return "Rinetd运行中"

class Index():
    def GET(self):
        result = getConf()
        port_state = commands.getoutput('netstat -lnt').split("\n")
        status = rinetd_state()
        return render.index(result, status, port_state, msg=None)

class Add():
    def POST(self):
        form = web.input()
        result = getConf()
        status = rinetd_state()
        port_state = commands.getoutput('netstat -lnt').split("\n")
        p = []
        for i,n in enumerate(port_state):
            if i > 1:
                s = ' '.join(n.split())
                p.append(s.split()[3].split(":")[-1])
        if form['SocIP'] != "" and form['SocPort'] != "" and form['DesIP'] != "" and form['DesPort'] != "":
            #result = ' '.join(form.values())
            for line in result.values():
                if line['SocPort'] == form['SocPort'] or form['SocPort'] in p:
                    msg = "端口已存在"
                    return render.index(result, status, port_state, msg)

            new_result = "%s %s %s %s" % (form['SocIP'], form['SocPort'], form['DesIP'], form['DesPort'])
            with open(CONF, mode='a') as data:
                data.write(new_result.encode("utf-8") + '\n')
            msg = "添加成功"
            return render.index(result, status, port_state, msg)
        else:
            msg = "不允许为空"
            return render.index(result, status, port_state, msg)


class Del():
    def POST(self):
        form = web.input()
        result = getConf()
        status = rinetd_state()
        port_state = commands.getoutput('netstat -lnt').split("\n")
        lists = []
        for line in result.values():
            lists.append(line['SocPort'])
        if form['SocIP'] != "" and form['SocPort'] != "" and form['DesIP'] != "" and form['DesPort'] != "":
            with open( CONF, 'r') as fobj:
                lines = fobj.readlines()
            for line in lines:
                line = line.strip('\n')
                new_result = line.split(" ")[1]
                if form['SocPort'] in lists and form['SocPort'] == new_result:
                    count = 0
                    while count < len(lines):
                        if  len(lines[count]) > 2 and new_result == lines[count].split(" ")[1]:
                            lines.pop(count)
                        else:
                            count += 1
                    with open( CONF, 'w') as wobj:
                        wobj.writelines(lines)
                print line
            msg = "删除成功"
            return render.index(result, status, port_state, msg)
        else:
            msg = "记录不存在"
            return render.index(result, status, port_state, msg)

class Operate():
    def POST(self,operate=None):
        form = web.input()
        result = getConf() 
        if form['pm'] == 'start':
            pid = commands.getoutput(PID)
            if pid != "":
                raise web.seeother('/')
            stats = subprocess.Popen( rinetd_bin + ' -c ' + CONF + ' &' , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            time.sleep(0.3) 
            raise web.seeother('/')
        elif form['pm'] == 'stop':
            pid = commands.getoutput(PID)
            if pid == "":
                raise web.seeother('/')
            commands.getstatusoutput('killall rinetd')
            raise web.seeother('/')
        elif form['pm'] == 'reload':
            pid = commands.getoutput(PID)
            if pid == "":
                raise web.seeother('/')
            commands.getstatusoutput("kill -1 `ps -elf |grep rinetd|grep -v grep |awk '{print $4}'`")
            time.sleep(0.3)
            raise web.seeother('/')

application = app.wsgifunc()
