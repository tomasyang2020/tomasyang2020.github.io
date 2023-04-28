# coding:utf-8

import datetime
import requests
from pyquery import PyQuery as pq

def pushBlog(trendtype):
    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/trending?since={trendtype}'.format(trendtype=trendtype)
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200
    
    d = pq(r.content)
    items = d('div.Box article.Box-row')

    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    todaytitle ="---\nlayout: post\ntitle: 【Bot】Github 趋势" + strdate + "\n---\n\n"
    contents = todaytitle
    for item in items:
        i = pq(item)
        title = i(".lh-condensed a").text()
        description = i("p.col-9").text()
        url = i(".lh-condensed a").attr("href")
        url = "https://github.com" + url
        if "zhao" in url:
            continue
        linecontent = u"* [{title}]({url}):{description}".format(title=title, url=url, description=description)
        contents+= linecontent.replace('\n','')+"\n"
    mdfilename="_posts/{date}-Bot-GithubTrending-{date}.md".format(date=strdate)
    with open(mdfilename, 'w') as f:
        f.write(contents)


def job():
    pushBlog('daily')


if __name__ == '__main__':
    job()
