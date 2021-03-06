# -*- coding: UTF-8 -*-

import operator
import json
import os
import time
import re
import requests
import ConfigParser
import sys
import xlwt
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')

Zhihu = 'http://www.zhihu.com'
header_info = {
    "Accept": "*/*",
    "Accept-Encoding":"gzip,deflate,sdch",
    "Accept-Language":"zh-CN,zh;q=0.8",
    "Connection":"keep-alive",
    "Connect-Length":"127",
    "Connect-type":"application/x-www-form-urlencoded; charset=UTF-8",
    "DNT":"1",
    "Host":"www.zhihu.com",
    "Origin":"http://www.zhihu.com",
    "Referer":"http://www.zhihu.com/people/xiaofeng-tong-xue/followers",
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "X-Requested-With":"XMLHttpRequest",
}

def login():
    url = 'http://www.zhihu.com'
    loginurl = 'http://www.zhihu.com/login/email'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Host': 'www.zhihu.com',
        'Referer': 'http://www.zhihu.com/',
    }

    data = {
        'email': '861005532@qq.com',
        'password': '86100major5532',
        'rememberme': 'true',
    }

    global s
    s = requests.session()
    req = s.get(url, headers=headers)
    print req

    soup = BeautifulSoup(req.text, "html.parser")
    global xsrf
    xsrf = soup.find('input', {'name': '_xsrf', 'type': 'hidden'}).get('value')
    data['_xsrf'] = xsrf

    timestamp = int(time.time() * 1000)
    captchaURL = 'http://www.zhihu.com/captcha.gif?=' + str(timestamp)
    print captchaURL

    with open('zhihucaptcha.gif', 'wb') as f:
        captchaREQ = s.get(captchaURL)
        f.write(captchaREQ.content)
    # loginCaptcha = raw_input('input captcha:\n').strip()
    loginCaptcha = str(timestamp)
    data['captcha'] = loginCaptcha
    print data
    loginREQ = s.post(loginurl, headers=headers, data=data)
    if not loginREQ.json()['r']:
        print s.cookies.get_dict()
        with open('cookiefile', 'wb') as f:
            json.dump(s.cookies.get_dict(), f)
    else:
        print 'login fail'


def get_voters(ans_id):
    # 直接输入问题id(这个id在点击“等人赞同”时可以通过监听网络得到)，关注者保存在以问题id命名的.txt文件中
    login()
    file_name = str(ans_id) + '.txt'
    f = open(file_name, 'w')
    source_url = Zhihu + '/answer/' +str(ans_id) +'/voters_profile'
    source = s.get(source_url)
    print source
    content = source.content
    print content    # json语句
    data = json.loads(content)   # 包含总赞数、一组点赞者的信息、指向下一组点赞者的资源等的数据
    # 打印总赞数
    txt1 = '总赞数'
    print txt1.decode('utf-8')
    total = data['paging']['total']   # 总赞数
    print data['paging']['total']   # 总赞数
    # 通过分析，每一组资源包含10个点赞者的信息（当然，最后一组可能少于10个），所以需要循环遍历
    nextsource_url = source_url     # 从第0组点赞者开始解析
    num = 0
    while nextsource_url!=Zhihu:
        try:
            nextsource = s.get(nextsource_url)
        except:
            time.sleep(2)
            nextsource = s.get(nextsource_url)
        # 解析出点赞者的信息
        nextcontent = nextsource.content
        nextdata = json.loads(nextcontent)
        # 打印每个点赞者的信息
        # txt2 = '打印每个点赞者的信息'
        # print txt2.decode('utf-8')
        # 提取每个点赞者的基本信息
        for each in nextdata['payload']:
            num += 1
            print num
            try:
                soup = BeautifulSoup(each, 'lxml')
                tag = soup.a
                title = tag['title']    # 点赞者的用户名
                href = 'http://www.zhihu.com' + str(tag['href'])    # 点赞者的地址
                # 获取点赞者的数据
                list = soup.find_all('li')
                votes = list[0].string  # 点赞者获取的赞同
                tks = list[1].string  # 点赞者获取的感谢
                ques = list[2].string  # 点赞者提出的问题数量
                ans = list[3].string  # 点赞者回答的问题数量
                # 打印点赞者信息
                string = title + '  ' + href + '  ' + votes + tks + ques + ans
                f.write(string + '\n')
                print string
            except:
                txt3 = '有点赞者的信息缺失'
                f.write(txt3.decode('utf-8') + '\n')
                print txt3.decode('utf-8')
                continue
        # 解析出指向下一组点赞者的资源
        nextsource_url = Zhihu + nextdata['paging']['next']
    f.close()


def text(ans_id):
    # 检查有多少点赞者的信息没有提取出来
    start = time.clock()
    # ans_id = 13942420   #问题id
    file_name = str(ans_id) + '.txt'
    f = open(file_name, 'r')
    string = f.readline()
    num1 = 0 # 计数器1，记录总的点赞人数
    num2 = 0 # 计数器2，记录信息缺失者的人数
    txt = '有点赞者的信息缺失\n'
    while string:
        try:
            print string.decode('utf-8')
        except:
            print string
        print len(string)
        if len(string) == 28:
            num2 += 1
        num1 += 1
        print num1
        string = f.readline()
    txt1 = '总的点赞人数：'
    txt2 = '信息缺失者的人数：'
    print txt1.decode('utf-8') + str(num1)
    print txt2.decode('utf-8') + str(num2)
    print float(num2)/float(num1)
    end = time.clock()
    print 'Time consumption: %f s' % (end-start)


def has_attrs(tag):
    return tag.has_attr('target') and tag.has_attr('href') and tag.has_attr('class')

def get_followers(username):
    # 直接输入用户名，关注者保存在以用户名命名的.txt文件中
    followers_url = 'http://www.zhihu.com/people/' + username + '/followers'
    file_name = username + '.txt'
    f = open(file_name, 'w')
    data = s.get(followers_url)
    print data  # 访问服务器成功，返回<responce 200>
    content = data.content  # 提取出html信息
    soup = BeautifulSoup(content, "lxml")   # 对html信息进行解析
    # 获取关注者数量
    totalsen = soup.select('span[class*="zm-profile-section-name"]')
    total = int(str(totalsen[0]).split(' ')[4])     # 总的关注者数量
    txt1 = '总的关注者人数：'
    print txt1.decode('utf-8')
    print total
    follist = soup.select('div[class*="zm-profile-card"]')  # 记录有关注者信息的list
    num = 0 # 用来在下面显示正在查询第多少个关注者
    for follower in follist:
        tag =follower.a
        title = tag['title']    # 用户名
        href = 'http://www.zhihu.com' + str(tag['href'])    # 用户地址
        # 获取用户数据
        num +=1
        print num
        Alist = follower.find_all(has_attrs)
        votes = Alist[0].string  # 点赞者获取的赞同
        tks = Alist[1].string  # 点赞者获取的感谢
        ques = Alist[2].string  # 点赞者提出的问题数量
        ans = Alist[3].string  # 点赞者回答的问题数量
        # 打印关注者信息
        string = title + '  ' + href + '  ' + votes + tks + ques + ans
        try:
            print string.decode('utf-8')
        except:
            print string.encode('gbk', 'ignore')
        f.write(string + '\n')

    # 循环次数
    n = total/20-1 if total/20.0-total/20 == 0 else total/20
    for i in range(1, n+1, 1):
        raw_hash_id = re.findall('hash_id(.*)', content)
        hash_id = raw_hash_id[0][14:46]
        _xsrf = xsrf
        offset = 20*i
        params = json.dumps({"offset": offset, "order_by": "created", "hash_id": hash_id})
        payload = {"method":"next", "params": params, "_xsrf": _xsrf}
        click_url = 'http://www.zhihu.com/node/ProfileFollowersListV2'
        data = s.post(click_url, data=payload, headers=header_info)
        # print data
        source = json.loads(data.content)
        for follower in source['msg']:
            soup1 = BeautifulSoup(follower, 'lxml')
            tag =soup1.a
            title = tag['title']    # 用户名
            href = 'http://www.zhihu.com' + str(tag['href'])    # 用户地址
            # 获取用户数据
            num +=1
            print num
            Alist = soup1.find_all(has_attrs)
            votes = Alist[0].string  # 点赞者获取的赞同
            tks = Alist[1].string  # 点赞者获取的感谢
            ques = Alist[2].string  # 点赞者提出的问题数量
            ans = Alist[3].string  # 点赞者回答的问题数量
            # 打印关注者信息
            string = title + '  ' + href + '  ' + votes + tks + ques + ans
            try:
                print string.decode('utf-8')
            except:
                print string.encode('gbk', 'ignore')
            f.write(string + '\n')
    f.close()
    
    
def parse_followers_education(filename):
    # 将followers的信息从文件中提取出来，解析出教育信息
    dict_education_item = {}    # 存储数据
    dict_education_extra_item = {}
    txt1 = 'no education item'
    txt2 = 'no education-extra item'
    filename = r'E:\PythonWorkspace\liu-xiao-liu-9-24--followers.txt'
    f = open(filename, 'r')
    info = f.readline()
    num = 1 # 计数器
    # print info.encode('gbk', 'ignore')
    # print str(info.split('  ')[1])
    while info:
        print num
        print str(info.split('  ')[0]).encode('gbk', 'ignore')
        print info.split('  ')[1]
        # 提取education-item
        url = info.split('  ')[1]
        data = s.get(url)
        soup = BeautifulSoup(data.content, 'lxml')
        try:
            education_item = soup.find('span', class_='education item').string
        except:
            education_item = txt1
        print education_item
        if education_item not in dict_education_item.keys():
            dict_education_item[education_item] = 0
        dict_education_item[education_item] += 1
        try:
            education_extra_item = soup.find('span', class_='education-extra item').string
        except:
            education_extra_item = txt2
        print education_extra_item
        if education_extra_item not in dict_education_extra_item.keys():
            dict_education_extra_item[education_extra_item] = 0
        dict_education_extra_item[education_extra_item] += 1
        info = f.readline()
        num += 1
    # 对数据进行排序输出
    dict_education_item = sorted(dict_education_item.iteritems(), key=operator.itemgetter(1), reverse=True)
    print str(dict_education_item).decode('unicode-escape')
    print '\n'
    dict_education_extra_item = sorted(dict_education_extra_item.iteritems(), key=operator.itemgetter(1), reverse=True)
    print str(dict_education_extra_item).decode('unicode-escape')



def get_answer(question_num):
    url = 'http://www.zhihu.com/question/' + str(question_num)
    data = s.get(url)
    soup = BeautifulSoup(data.content, 'lxml')
    # print str(soup).encode('gbk', 'ignore')
    title = soup.title.string.split('\n')[2]    # 问题题目
    path = 'E://zhihu/' + title
    if not os.path.isdir(path):
        os.mkdir(path)
    description = soup.find('div', {'class': 'zm-editable-content'}).strings    # 问题描述，可能多行
    file_name = path + '/description.txt'
    fw = open(file_name, 'w')
    for each in description:
        each = each + '\n'
        fw.write(each)
    # description = soup.find('div', {'class': 'zm-editable-content'}).get_text() # 问题描述
        # 调用.string属性返回None（可能是因为有换行符在内的缘故）,调用get_text()方法得到了文本，但换行丢了
    answer_num = int(soup.find('h3', {'id': 'zh-question-answer-num'}).string.split(' ')[0]) # 答案数量
    num = 1
    index = soup.find_all('div', {'tabindex': '-1'})
    for i in range(len(index)):
        try:
            a = index[i].find('a', {'class': 'author-link'})
            title = str(num) + '__' + a.string
            href = 'http://www.zhihu.com' + a['href']
        except:
            title = str(num) + '__匿名用户'
        answer_file_name = path + '/' + title + '__.txt'
        fr = open(answer_file_name, 'w')
        try:
            answer_content = index[i].find('div', {'class': 'zm-editable-content clearfix'}).strings
        except:
            answer_content = ['作者修改内容通过后，回答会重新显示。如果一周内未得到有效修改，回答会自动折叠。']
        for content in answer_content:
            fr.write(content + '\n')
        num += 1

    _xsrf = xsrf
    url_token = re.findall('url_token(.*)', data.content)[0][8:16]
    # 循环次数
    n = answer_num/20-1 if answer_num/20.0-answer_num/20 == 0 else answer_num/20
    for i in range(1, n+1, 1):
        # _xsrf = xsrf
        # url_token = re.findall('url_token(.*)', data.content)[0][8:16]
        offset = 20*i
        params = json.dumps({"url_token": url_token, "pagesize": 20, "offset": offset})
        payload = {"method":"next", "params": params, "_xsrf": _xsrf}
        click_url = 'https://www.zhihu.com/node/QuestionAnswerListV2'
        data = s.post(click_url, data=payload, headers=header_info)
        data = json.loads(data.content)
        for answer in data['msg']:
            print ('正在提取第' + str(num) + '个答案......').encode('gbk', 'ignore')
            soup1 = BeautifulSoup(answer, 'lxml')
            try:
                a = soup1.find('a', {'class': 'author-link'})
                title = str(num) + '__' + a.string
                href = 'http://www.zhihu.com' + a['href']
            except:
                title = str(num) + '__匿名用户'
            answer_file_name = path + '/' + title + '__.txt'
            fr = open(answer_file_name, 'w')
            try:
                answer_content = soup1.find('div', {'class': 'zm-editable-content clearfix'}).strings
            except:
                answer_content = ['作者修改内容通过后，回答会重新显示。如果一周内未得到有效修改，回答会自动折叠。']
            for content in answer_content:
                fr.write(content + '\n')
            num += 1
