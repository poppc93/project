from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
def getTitle(url):
    try:
        html = urlopen(url)
    except HTPPError as e:
        return None
    try:
        bs0bj = BeautifulSoup(html.read(), "html.parser")
        title = bs0bj.find_all('ul', 'slist1')
    except AttributeError as e:
        return None
    return title

title = getTitle("http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=101")
if title == None:
    print("Title could not be found")
else:
    for n in title:
        print(n.get_text()) #text만 골라내기
