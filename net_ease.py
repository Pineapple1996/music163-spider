# -*- coding: utf-8 -*-

# -------------------------------------------------
# @Time    : 6/13/19 6:38 PM
# @Author  : Pineapple1996
# @File    : net_ease.py
# -------------------------------------------------
import copy
import json
import logging
import time
from pyquery import PyQuery as pq
import requests


def get_albums(url):
    err_count = 0
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    resp = ''
    while err_count < 20:
        try:
            resp = requests.get(url, headers=headers, timeout=2)
        except requests.exceptions.ConnectTimeout:
            time.sleep(2)
            continue
        except requests.exceptions.Timeout:
            time.sleep(2)
            continue
        except Exception as e:
            logging.error(e)
            time.sleep(2)
            err_count += 1
            continue
        break
    if not resp:
        return  None,False
    else:
        html = resp.text
        # print(html)
        pq_rt = pq(html)
        div = pq_rt('#m-song-module li ')
        album_list = []
        for i in range(len(div)):
            li = (div.eq(i))
            tit =li('.tit').text()
            date = li('.s-fc3').text()
            album_url = 'https://music.163.com'+li('.tit').attr('href')
            # print(tit,date,album_url)
            temp = {'album_tit':tit,'album_date':date,'album_url':album_url}
            album_list.append(temp)
        next_page = True
        if len(div) <12:
            next_page = False
        return album_list,next_page

def get_album_songs(url,album_data):
    err_count = 0
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    while err_count < 20:
        try:
            resp = requests.get(url, headers=headers, timeout=2)
        except requests.exceptions.ConnectTimeout:
            time.sleep(2)
            continue
        except requests.exceptions.Timeout:
            time.sleep(2)
            continue
        except Exception as e:
            logging.error(e)
            time.sleep(2)
            err_count += 1
            continue
        break
    if not resp:
        return
    html = resp.text
    pq_rt = pq(html)
    div = pq_rt('.f-hide li ')
    result = []
    # temp = (album_data)
    for i in range(len(div)):
        temp = album_data.copy()
        # print(temp)
        li = (div.eq(i))
        song_name = li('a').text()
        song_url = li('a').attr('href')
        print(song_name,song_url)
        temp['song_name'] = song_name
        temp['song_url'] = 'https://music.163.com'+song_url
        song_id = song_url.replace('/song?id=','')
        lyric = get_lyric(song_id)
        temp['lyric'] = lyric
        result.append(temp)
    return result

def get_lyric(id):
    url = 'http://music.163.com/api/song/media?id={}'.format(id)
    err_count = 0
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    while err_count < 20:
        try:
            resp = requests.get(url, headers=headers, timeout=2)
        except requests.exceptions.ConnectTimeout:
            time.sleep(2)
            continue
        except requests.exceptions.Timeout:
            time.sleep(2)
            continue
        except Exception as e:
            logging.error(e)
            time.sleep(2)
            err_count += 1
            continue
        break
    if not resp:
        return
    try:
        js_data = json.loads(resp.text)
    except Exception as e:
        print(e)
    try :
        result = js_data['lyric']
    except Exception as e:
        print(e,url)
        result=''
    return result


if __name__ == '__main__':
    next_page =True
    page =0
    with open('song_data.json','w') as f:
        while next_page:

            url = 'https://music.163.com/artist/album?id=3684&limit=12&offset={}'.format(page*12)  # 专辑
            album_list, next_page = get_albums(url)
            if not album_list:
                next_page =True
                continue
            page+=1

            for data in album_list:

                album_url = data['album_url']
                result = get_album_songs(album_url,data)
                for wd in result:
                    f.write(json.dumps(wd,ensure_ascii=False))
                    f.write('\n')
                    f.flush()
            # break