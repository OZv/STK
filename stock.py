#!/usr/bin/env python
# -*- coding: utf-8 -*-
## stock.py
## A helpful tool to fetch data from website
##
## This program is a free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, version 3 of the License.
##
## You can get a copy of GNU General Public License along this program
## But you can always get it from http://www.gnu.org/licenses/gpl.txt
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
import os
import re
import json
import requests
from os import path
import datetime
from collections import OrderedDict


def fullpath(file, suffix='', base_dir=''):
    if base_dir:
        return ''.join([os.getcwd(), path.sep, base_dir, file, suffix])
    else:
        return ''.join([os.getcwd(), path.sep, file, suffix])


def readdata(file, base_dir=''):
    fp = fullpath(file, base_dir=base_dir)
    if not path.exists(fp):
        print("%s was not found." % fp)
    else:
        fr = open(fp, 'rU')
        try:
            return fr.read()
        finally:
            fr.close()
    return None


def dump(data, file, mod='w'):
    fname = fullpath(file)
    fw = open(fname, mod)
    try:
        fw.write(data)
    finally:
        fw.close()


def removefile(file):
    if path.exists(file):
        os.remove(file)


def info(l, s='code'):
    return '%d %ss' % (l, s) if l>1 else '%d %s' % (l, s)


def getcodelist(file, base_dir=''):
    text = readdata(file, base_dir)
    if text:
        p = re.compile(r'\s*\n\s*')
        text = p.sub('\n', text).strip()
        codes = OrderedDict()
        for code in text.split('\n'):
#            print code
            c, n, m, d = code.split('\t')
            codes[c] = (n, m, d)
        return codes
    print("%s: No such file or file content is empty." % file)
    return OrderedDict()


def getindex(file, base_dir=''):
    text = readdata(file, base_dir)
    if text:
        p = re.compile(r'\s*\n\s*')
        text = p.sub('\n', text).strip()
        codes = OrderedDict()
        for code in text.split('\n'):
            c, n = code.split('\t')
            codes[c] = n.strip()
        return codes
    print("%s: No such file or file content is empty." % file)
    return OrderedDict()


def getfaildlist(file, base_dir=''):
    codes = readdata(file, base_dir)
    codelist = OrderedDict()
    if codes:
        codes = re.compile(r'\s*\n\s*').sub('\n', codes).strip()
        for code in codes.split('\n'):
            codelist[code] = None
    else:
        print("%s: No such file or file content is empty." % file)
    return codelist


def getpage(link, BASE_URL=''):
    r = requests.get(''.join([BASE_URL, link]), timeout=10, allow_redirects=False)
    if r.status_code == 200:
        return r.content
    else:
        return None


def getchg(c, o):
    if c==0 or o==0:
        return 0
    return round((c-o)*100/o, 2)


class downloader:
#download data
    def __init__(self, name, codes):
        self.dir = ''.join([name, path.sep])
        self.hdir = ''.join([self.dir, 'html', path.sep])
        self.__codes = codes
        self.base_url = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id='

    def __make_url(self, code):
        if code[0] == '6':
            return ''.join([self.base_url, code, '1'])
        else:
            return ''.join([self.base_url, code, '2'])

    def __upd_base(self):
        base = 1
        cur = datetime.datetime.now()
        if cur.weekday() >= 5:
            cur = cur + datetime.timedelta(4-cur.weekday())
        self.__day = cur.strftime('%y%m%d_%a')
        if path.exists(self.dir):
            index = getindex('index.txt', self.dir)
            if self.__day in index:
                base = int(index[self.__day])
            else:
                for f in os.listdir(fullpath(self.dir)):
                    if re.compile(r'^\d+\.js$').search(f):
                        base += 1
                index[self.__day] = str(base)
        else:
            os.mkdir(fullpath(self.dir))
            index = {self.__day: str(base)}
        self.__base = base
        self.__index = index
        dump('\n'.join(['\t'.join([k, v]) for k, v in index.iteritems()]), ''.join([self.dir, 'index.txt']))

    def __mod(self, flag):
        return 'a' if flag else 'w'

    def __dumpwords(self, fn, buf, sfx='', finished=True):
        f = fullpath(fn, sfx, self.dir)
        if len(buf):
            mod = self.__mod(sfx)
            fw = open(f, mod)
            try:
                fw.write(json.dumps(buf, separators=(',', ':')))
            finally:
                fw.close()
        elif not path.exists(f):
            fw = open(f, 'w')
            fw.write('\n')
            fw.close()
        if sfx and finished:
            removefile(fullpath('failed.txt', '', self.dir))
            l = -len(sfx)
            cmd = '\1'
            nf = f[:l]
            if path.exists(nf):
                msg = "Found rawhtml.txt in the same dir, delete?(default=y/n)"
                cmd = 'y'#raw_input(msg)
            if cmd == 'n':
                return
            elif cmd != '\1':
                removefile(nf)
            os.rename(f, nf)

    def __fetchdata(self, fn, codes, suffix=''):
        count, buf, failed = 1, OrderedDict(), []
        leni = len(codes)
        while leni:
            for code in codes:
                if count % 100 == 0:
                    print ".",
                    if count % 500 == 0:
                        print count,
                try:
                    page = getpage(self.__make_url(code))
                    if page:
                        self.__getinfo(page, code, buf)
                        count += 1
                    else:
                        failed.append(code)
                except Exception, e:
                    import traceback
                    print traceback.print_exc()
                    print "%s failed, retry automatically later" % code
                    failed.append(code)
            lenr = len(failed)
            if lenr >= leni:
                break
            else:
                leni = lenr
                codes, failed = failed, []
        print "%s browsed" % info(count-1),
        if failed:
            dump('\n'.join(failed), ''.join([self.dir, 'failed.txt']))
            self.__dumpwords(fn, buf, '.part', False)
            return False
        else:
            print ", 0 code failed"
            self.__dumpwords(fn, buf, suffix)
            return True

    def __getinfo(self, page, code, buf):
        lb = '"Value":['
        i = page.find(lb)
        assert i>0
        page = page[i+len(lb):]
        vl = page.replace('"', '').split(',')
        if len(vl) > 34:
            close = float(vl[25])
            close = float(vl[34]) if close==0 else close
            aver = float(vl[26])
            open = float(vl[28])
            high = float(vl[30])
            low = float(vl[32])
            buf[code] = (open, close, high, low, aver)
        else:
            buf[code] = (0, 0, 0, 0, 0)

    def start(self):
        import socket
        socket.setdefaulttimeout(120)
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.__upd_base()
        fn = ''.join([str(self.__base), '.js'])
        fp1 = fullpath(fn, '.part', self.dir)
        fp2 = fullpath('failed.txt', base_dir=self.dir)
        fp3 = fullpath(fn, base_dir=self.dir)
        rst = True
        if path.exists(fp1) and path.exists(fp2):
            print ("Continue last failed")
            failed = getfaildlist('failed.txt', self.dir).keys()
            rst = self.__fetchdata(fn, failed, '.part')
        elif not path.exists(fp3):
            print ("New session started")
            rst = self.__fetchdata(fn, self.__codes)
        return rst

    def __make_th(self, curbase):
        html, i = [], 0
        for count in [3, 5, 10, 15, 20, 30, 60, 90, 120, 200]:
            if curbase > count:
                cls = ' class="oxc"' if i==0 else ''
                html.append(''.join(['<th', cls, '><span onclick="e8c(this,', str(i), ');">', str(count), '\xe6\x97\xa5</span></th>']))
                i += 1
        return html

    def __make_tbl(self, curbase):
        th = self.__make_th(curbase)
        html = ['<table class="tgq"><thead>',
        '<tr><th rowspan=2>\xe6\x8e\x92\xe5\x90\x8d</th><th rowspan=2>\xe4\xbb\xa3\xe7\xa0\x81</th><th rowspan=2>\xe5\x90\x8d\xe7\xa7\xb0</th><th rowspan=2>\xe6\xb6\xa8\xe5\xb9\x85</th><th rowspan=2>\xe7\x8e\xb0\xe4\xbb\xb7</th>',
        '<th colspan=', str(len(th)), '>\xe7\xb4\xaf\xe7\xa7\xaf\xe6\xb6\xa8\xe5\xb9\x85</th>',
        '<th rowspan=2>\xe8\xa1\x8c\xe4\xb8\x9a</th><th rowspan=2>\xe5\x9c\xb0\xe5\x9f\x9f</th></tr><tr id="tb8">']
        html.extend(th)
        html.append('</tr></thead><tbody></tbody></table>')
        return html

    def __calc_chg(self, codes, data, data_s):
        for code in data:
            if code in data_s:
                chg = getchg(data[code][1], data_s[code][1])
            else:
                chg = 0
            if code in codes:
                codes[code].append(chg)
            else:
                codes[code] = [chg]

    def __get_order(self, codes, x, n):
        sl, idx = [], 1
        sd = sorted(codes.items(), key=lambda d: d[1][x], reverse=True)
        for cd, v in sd:
            if len(sl) < 100:
                if n==0 or (n==1 and cd[0]=='6') or (n==2 and cd[0]!='6'):
                    sl.append(cd)
            if n==0:
                if codes[cd][-1] == 0:
                    codes[cd].append(-1)
                else:
                    codes[cd].append(idx)
            if n==0 or (n==1 and cd[0]=='6') or (n==2 and cd[0]!='6'):
                idx += 1
        return sl

    def __make_js(self, curbase):
        codes = OrderedDict()
        order, x = [[], [], []], 0
        data = json.loads(readdata(''.join([str(curbase), '.js']), self.dir))
        data_s1 = json.loads(readdata(''.join([str(curbase-1), '.js']), self.dir))
        for count in [3, 5, 10, 15, 20, 30, 60, 90, 120, 200]:
            if curbase > count:
                data_s = json.loads(readdata(''.join([str(curbase-count), '.js']), self.dir))
                self.__calc_chg(codes, data, data_s)
                for i in xrange(3):
                    order[i].append(self.__get_order(codes, x, i))
                x += 2
        dc = OrderedDict()
        for ml in order:
            for ol in ml:
                for od in ol:
                    if not od in dc:
                        if od in data_s1:
                            chg = getchg(data[od][1], data_s1[od][1])
                        else:
                            chg = 0
                        dc[od] = [chg, data[od][1]]
                        dc[od].extend(codes[od])
        vc = ''.join(['var vc=', json.dumps(dc, separators=(',', ':')), ';\n'])
        vo = ''.join(['var vo=', json.dumps(order, separators=(',', ':')), ';\n'])
        return [vc, vo]

    def __gen_html(self, base, day, pre, nxt):
        fh = ''.join([self.hdir, day, '.html'])
        if path.exists(fullpath(fh)):
            return
        html = ['<html><head><meta http-equiv="content-type" content="text/html;charset=utf-8">',
        '<link rel="stylesheet" href="stock.css" type="text/css"><script type="text/javascript" src="func.js"></script>',
        '<script type="text/javascript" src="code.js"></script><script type="text/javascript">']
        html.extend(self.__make_js(base))
        html.extend(['</script></head><body><div class="buc">',
        '<div class="l7s"><span class="nwl" onclick="k9y(this,0);">\xe6\xb2\xaa\xe6\xb7\xb1</span>',
        '<span onclick="k9y(this,1);">\xe6\xb2\xaa\xe5\xb8\x82</span>',
        '<span onclick="k9y(this,2);">\xe6\xb7\xb1\xe5\xb8\x82</span></div>',
        '<div class="sk7">', re.compile('(\d{2})(\d{2})(\d{2})_(\w{3})').sub(r'20\1/\2/\3, \4', day), '</div>',
        '<div class="mhp">'])
        if pre:
            LK = ''.join(['<a href="', pre, '.html">%s</a><a href="', nxt, '.html">%s</a>'])
        else:
            LK = ''.join(['<span>%s</span><a href="', nxt, '.html">%s</a>'])
        html.append(LK % ('&lt;&lt;\xe5\x89\x8d\xe4\xb8\x80\xe5\xa4\xa9', '\xe5\x90\x8e\xe4\xb8\x80\xe5\xa4\xa9&gt;&gt;'))
        html.append('</div>')
        html.extend(self.__make_tbl(base))
        html.append('</div></body></html>')
        dump(''.join(html), fh)

    def format(self):
        if not path.exists(fullpath(self.hdir)):
            os.mkdir(fullpath(self.hdir))
        fc = ''.join([self.hdir, 'code.js'])
        if not path.exists(fullpath(fc)):
            db = OrderedDict()
            for code, v in self.__codes.iteritems():
                db[code] = [v[0], v[1], v[2]]
            dump(''.join(['var cl=', json.dumps(db, separators=(',', ':'), ensure_ascii=False), ';']), fc)
        days, pre, next = self.__index.keys(), '', ''
        for i in xrange(len(self.__index)):
            day = days[i]
            if day == self.__day:
                nxt = datetime.datetime.strptime(day, '%y%m%d_%a').date() + datetime.timedelta(1)
                if nxt.weekday() > 4:
                    nxt = nxt + datetime.timedelta(7-nxt.weekday())
                nxt = nxt.strftime('%y%m%d_%a')
            else:
                nxt = days[i+1]
            base = int(self.__index[day])
            if base > 3:
                self.__gen_html(base, day, pre, nxt)
                pre = day
        dump(''.join(['<html><head><meta http-equiv="refresh" content="0;url=', self.__day,
        '.html"><link rel="shortcut icon" href="favicon.png" type="image/x-png"></head></html>']),
        ''.join([self.hdir, 'index.html']))

if __name__=="__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    print "Start at %s" % datetime.datetime.now()
    sdl = downloader('stock', getcodelist('code.txt'))
    if sdl.start():
        sdl.format()
    print "Finished at %s" % datetime.datetime.now()
    cmd = raw_input("Press Enter to exit...")
    if cmd:
        pass
