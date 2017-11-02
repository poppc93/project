from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime
import random
random.seed(datetime.datetime.now())

def getTitle(url):
    try:
        html = urlopen(url)
    except HTPPError as e:
        return None
    try:
        bs0bj = BeautifulSoup(html.read(), "html.parser")
        title = bs0bj.find_all("div", {"id":"articleBodyContents"})
    except AttributeError as e:
        return None
    return title

def getArticleLinks(articleURL):
    html = urlopen("http://news.naver.com/main"+articleURL)
    bs0bj = BeautifulSoup(html, "html.parser")
    return bs0bj.find("div", {"class":"section_body"}).findAll("a", href=re.compile("^(http://news.naver.com/main/read)"))




links = getArticleLinks("/main.nhn?mode=LSD&mid=shm&sid1=101")
for a in links:
    title = getTitle(a.attrs['href'])
    print(title)
