#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from lxml import html
from Crypto.Cipher import AES
import base64
import requests
import json
import codecs
import time
import random 
import urllib2  

# 头部信息
headers = {
    'Host':"music.163.com",
    'Accept-Language':"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    'Accept-Encoding':"gzip, deflate",
    'Content-Type':"application/x-www-form-urlencoded",
    'Connection':"keep-alive",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36",
    'Referer':'http://music.163.com/'
    
}

url="http://music.163.com/"  
# proxies=["111.195.228.237:8123",'http://110.189.207.29:28412','http://121.205.254.42:808',
#          "121.232.146.143:9000",
#          "223.247.207.173:8998",
#          "218.104.148.157:8080",
#          "122.236.168.156:8998",
#         'http://183.32.88.182:808',
#         'http://219.138.58.167:3128',
#          'http://121.226.161.90:808',
#          'http://118.254.124.200:808',
#          'http://58.22.101.138:808',
#          'http://114.230.96.132:43840',
#          'http://171.37.160.99:8123'
#          ]
# 设置代理服务器
def get_ip_list(url, headers):
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list
#随机代理ip
def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append(ip)
    proxy_ip = random.choice(proxy_list)

    return proxy_ip


headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

ip_list = get_ip_list('http://www.xicidaili.com/nn/', headers=headers2)


def changable_proxies():
    proxies = get_random_ip(ip_list)
    print proxies
    return proxies
# offset的取值为:(评论页数-1)*20,total第一页为true，其余页为false
# first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}' # 第一个参数
second_param = "010001" # 第二个参数
# 第三个参数
third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
# 第四个参数
forth_param = "0CoJUm6Qyw8W8jud"


 
# 获取参数
def get_params(page): # page为传入页数
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    if(page == 1): # 如果为第一页
        first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
        h_encText = AES_encrypt(first_param, first_key, iv)
    else:
        offset = str((page-1)*20)
        first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' %(offset,'false')
        h_encText = AES_encrypt(first_param, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText
 
# 获取 encSecKey
def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey
 
 
# 解密过程
def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text


# 获得评论json数据
def get_json(url, params, encSecKey):
    data = {
         "params": params,
         "encSecKey": encSecKey
    }


    try:
     response = requests.post(url, headers=headers, data=data,proxies = changable_proxies())
    except Exception as e:
     print(e)
     s = requests.session()
     s.keep_alive = False
    # response = requests.post(url, headers=headers, data=data,proxies = proxies)
    return response.content
 
# 抓取热门评论，返回热评列表
def get_hot_comments(url):
    hot_comments_list = []
    hot_comments_list.append(u"用户ID 用户昵称 用户头像地址 评论时间 点赞总数 评论内容\n")
    params = get_params(1) # 第一页
    encSecKey = get_encSecKey()
    json_text = get_json(url,params,encSecKey)
    json_dict = json.loads(json_text)
    hot_comments = json_dict['hotComments'] # 热门评论
    print("共有%d条热门评论!" % len(hot_comments))
    for item in hot_comments:
            comment = item['content'] # 评论内容
            likedCount = item['likedCount'] # 点赞总数
            comment_time = item['time'] # 评论时间(时间戳)
            userID = item['user']['userID'] # 评论者id
            nickname = item['user']['nickname'] # 昵称
            avatarUrl = item['user']['avatarUrl'] # 头像地址
            comment_info = userID + " " + nickname + " " + avatarUrl + " " + comment_time + " " + likedCount + " " + comment + u"\n"
            hot_comments_list.append(comment_info)
    return hot_comments_list
 
# 抓取某一首歌的全部评论
def get_all_comments(url):
    all_comments_list = [] # 存放所有评论
    all_comments_list.append(u"用户ID 用户昵称 用户头像地址 评论时间 点赞总数 评论内容\n") # 头部信息
    params = get_params(1)
    encSecKey = get_encSecKey()
    json_text = get_json(url,params,encSecKey)
    json_dict = json.loads(json_text)
    comments_num = int(json_dict['total'])
    if(comments_num % 20 == 0):
        page = comments_num / 20
    else:
        page = int(comments_num / 20) + 1
    print("共有%d页评论!" % page)
    global mach
    mach = page
    for i in range(page):  # 逐页抓
        #if(i%500==0):
         # time.sleep(100)
          #time.sleep(int(format(random.randint(0,3))))
        params = get_params(i+1)
        encSecKey = get_encSecKey()
        json_text = get_json(url,params,encSecKey)
        json_dict = json.loads(json_text)
        if i == 0:
            print("共有%d条评论!" % comments_num) # 全部评论总数
        for item in json_dict['comments']:
            comment = item['content'] # 评论内容
            likedCount = item['likedCount'] # 点赞总数
            comment_time = item['time'] # 评论时间(时间戳)
            userID = item['user']['userId'] # 评论者id
            nickname = item['user']['nickname'] # 昵称
            avatarUrl = item['user']['avatarUrl'] # 头像地址
            comment_info = unicode(userID) + u" " + nickname + u" " + avatarUrl + u" " + unicode(comment_time) + u" " + unicode(likedCount) + u" " + comment + u"\n"
            all_comments_list.append(comment_info)
        print("第%d页抓取完毕!" % (i+1))
    return all_comments_list
 
 
# 将评论写入文本文件
def save_to_file(list,filename):
        with codecs.open(filename,'a',encoding='utf-8') as f:
            f.writelines(list)
        print("写入文件成功!")

#
# def getSongs(id):  # 这里的id是歌单的id
#     listurl = 'http://music.163.com/playlist?id=' + id
#     r = requests.get(listurl)
#
#     tree = html.fromstring(r.text)
#     data_json = tree.xpath('//textarea[@style="display:none;"]')[0].text
#
#     songs = json.loads(data_json)
#     return songs

if __name__ == "__main__":
    # songs=getSongs('961076463')
    # for song in songs:
    #     songid=str(song['id'])
    #     songname=str(song['name'])
    #     start_time = time.time() # 开始时间
    #     url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_"+songid+"/?csrf_token="
    #     filename = song['artists'][0]['name']+"-"+song['name']+u".txt"
    #     all_comments_list = get_all_comments(url)
    #     save_to_file(all_comments_list,filename)
    #     end_time = time.time() #结束时间
    #     print song['artists'][0]['name']+"-"+song['name']+'已抓取完毕！'
    #     print("程序耗时%f秒." % (end_time - start_time))
    start_time = time.time()  # 开始时间

    url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_186016/?csrf_token="
    filename = u"晴天.txt"
    all_comments_list = get_all_comments(url)
    save_to_file(all_comments_list, filename)
    end_time = time.time()  # 结束时间
    print("程序耗时%f秒." % (end_time - start_time))

