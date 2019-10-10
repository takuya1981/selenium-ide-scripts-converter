#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import os
import hashlib
import os.path
import glob
import codecs
from bs4 import BeautifulSoup

def conv(dir_in, project_name, file_out):
    CONVERT_TABLE = {"clickAndWait":"click", "selectAndWait":"select"}
    htmls = list_test_files(dir_in)
    tests = []
    tests_id = []
    urls = set()
    
    if len(htmls) == 0:
        print 'HTML files does not exist.'
        return

    for file in htmls:
        html = ''
        with open(file) as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        urls.add(soup.find('link').get('href'))
        commands = []
        for tr in soup.find('tbody').find_all("tr"):
            tds = tr.find_all('td')
            command = tds[0].string
            if CONVERT_TABLE.has_key(tds[0].string):
                command = CONVERT_TABLE[tds[0].string]

            commands.append(create_command(command, '', tds[1].string, '', tds[2].string))
        
        test = create_test(soup.find('thead').find('tr').find('td').string, commands)
        tests_id.append(test['id'])
        tests.append(test)
    
    urls_list = list(urls)
    suites = []
    suites.append(create_suite('Default Suite', tests_id))
    project = create_project(project_name, '' if len(urls_list) == 0 else urls_list[0], tests, suites, urls_list, [])
    
    with codecs.open(file_out, mode='w', encoding='utf-8') as f:
        f.write(json.dumps(project))

def list_test_files(dir_in):
    return glob.glob(os.path.join(dir_in, '*.html'))

# createt selenium script
def create_project(name, url, tests, suites, urls, plugins):
    p = {}
    p['id'] = gen_id()
    p['version'] = '2.0'
    p['name'] = name
    p['url'] = url
    p['tests'] = tests
    p['suites'] = suites
    p['urls'] = urls
    p['plugins'] = plugins
    return p

def create_suite(name, tests, persistSession = False, parallel = False, timeout = 300):
    s = {}
    s['id'] = gen_id()
    s['name'] = name
    s['persistSession'] = 'true' if persistSession else 'false'
    s['parallel'] = 'true' if parallel else 'false'
    s['timeout'] = timeout
    s['tests'] = tests
    return s

def create_test(name, commands):
    t = {}
    t['id'] = gen_id()
    t['name'] = name
    t['commands'] = commands
    return t

def create_command(command, comment, target, targets, value):
    c = {}
    c['id'] = gen_id()
    c['command'] = command
    c['comment'] = comment
    c['target'] = target
    c['targets'] = targets
    c['value'] = value
    return c

#generate random number for id of selenium script
def gen_rand_str_hex(length):
    buf = ''
    while len(buf) < length:
        buf += hashlib.md5(os.urandom(100)).hexdigest()
    return buf[0:length]

def gen_id():
    return gen_rand_str_hex(8) + '-' + gen_rand_str_hex(4) + '-' + gen_rand_str_hex(4) + '-' + gen_rand_str_hex(4) + '-' + gen_rand_str_hex(12)

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 4:
        print 'Usage: python selenium_convert.py dir_in project_name file_out'
        print 'args:'
        print '    dir_in: Directory containing old Selenium IDE scripts(.html) ' \
            'that were running before Firefox 55'
        print '    project_name: Selenium project name that you want to specify'
        print '    file_out: Converted script file(.side) path'
    else:
        conv(args[1], args[2], args[3])
