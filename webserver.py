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
    for line in fileinput.input("conf/rinetd.conf", inplace=1):
        line = line.strip('\n')
        result[i] = line
        i += 1
        print line

    k = ['SocIP', 'SocPort', 'DesIP', 'DesPort']
    for line in result.keys():
        v = str(result[line]).split()
        result[line] = dict(zip(k, v))
    fileinput.close()
    return result

def rinetd_state():
    pid = commands.getoutput('cat conf/rinetd.pid')
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
            with open("conf/rinetd.conf", mode='a') as data:
                data.write(new_result)
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
            for line in fileinput.input("conf/rinetd.conf", inplace=1):
                line = line.strip('\n')
                new_result = line.split(" ")[1]
                if form['SocPort'] in lists and form['SocPort'] == new_result:
                    continue
                print line
            fileinput.close()
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
            pid = commands.getoutput('cat conf/rinetd.pid')
            if pid != "":
                raise web.seeother('/')
            #args = shlex.split('%s -c %s/conf/rinetd.conf' % (rinetd_bin, BASE_DIR))
            stats = subprocess.Popen('%s -c conf/rinetd.conf' % rinetd_bin, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            with open("conf/rinetd.pid", mode='w') as data:
                data.write(str(stats.pid)) 
                data.close()

            time.sleep(0.3) 
            #status = rinetd_state()
            #port_state = commands.getoutput('netstat -lnt').split("\n")
            #msg = "启动成功"
            #return render.index(result, status, port_state, msg)
            raise web.seeother('/')
        elif form['pm'] == 'stop':
            pid = commands.getoutput('cat conf/rinetd.pid')
            if pid == "":
                raise web.seeother('/')
            commands.getstatusoutput('killall rinetd')
            commands.getoutput('> conf/rinetd.pid')
            
            #status = rinetd_state()
            #port_state = commands.getoutput('netstat -lnt').split("\n")
            #msg = "停止成功"
            #return render.index(result, status, port_state, msg)
            raise web.seeother('/')
        elif form['pm'] == 'reload':
            pid = commands.getoutput('cat conf/rinetd.pid')
            if pid == "":
                raise web.seeother('/')
            commands.getstatusoutput('killall rinetd')
            commands.getoutput('> conf/rinetd.pid')
            #args = shlex.split('%s -c %s/conf/rinetd.conf' % (rinetd_bin, BASE_DIR))
            stats = subprocess.Popen('%s -c conf/rinetd.conf' % rinetd_bin, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            with open("conf/rinetd.pid", mode='w') as data:
                data.write(str(stats.pid)) 
            
            time.sleep(0.3)
            #status = rinetd_state()
            #port_state = commands.getoutput('netstat -lnt').split("\n")
            #msg = "加载成功"
            #return render.index(result, status, port_state, msg)
            raise web.seeother('/')

application = app.wsgifunc()
