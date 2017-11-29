# music163-spider
网易云音乐歌曲评论爬虫

特点：

随机IP
```python
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
```