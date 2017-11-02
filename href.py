from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime
import random
random.seed(datetime.datetime.now())

def getBody(url):
    html = urlopen(url)
    bs0bj = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    body = ''
    for item in bs0bj.find_all('div', id='articleBodyContents'):
        body = body + str(item.find_all(text=True))
    return body

def getDate(url):
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    date= ''
    item = soup.find_all('span', {'class':'t11'})
    date = date +str(item[0].find_all(text=True))#첫번째 span태그만을 가져와서 text파일을 가져옴 ->즉 기사의 최초 작성 시기를 가져온다.
    date = re.sub('[\-:]', ' ', date) # : 과 - 를 공백으로 대체
    date = re.sub('[\'\[\]]', '', date) # '과 대괄호 제거
    return date

def clean(title):
    cleaned = re.sub('[A-Za-z0-9\._+]+@[A-Za-z]+\.(co.kr|com|net)', '', title) #이메일제거
    cleaned = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', cleaned) #기타기호 제거
    cleaned = re.sub('(nfunction flashremoveCallback|flash)', '', cleaned)
    cleaned = re.sub('(본문 내용|TV플레이어)', '', cleaned)
    cleaned = re.sub('(n )', '', cleaned)
    cleaned = re.sub('(오류를 우회하기 위한 함수 추가 )', '', cleaned)
    cleaned = re.sub('(           )', '', cleaned)
    
    return cleaned

def getArticleLinks(articleURL):
    html = urlopen("http://news.naver.com/main"+articleURL)
    bs0bj = BeautifulSoup(html, "html.parser")
    return bs0bj.find("div", {"class":"section_body"}).findAll("a", href=re.compile("^(http://news.naver.com/main/read)"))


links = getArticleLinks("/main.nhn?mode=LSD&mid=shm&sid1=101")

file = open("output.txt", 'a')
for a in links:
    hyperlink = a.attrs['href']
    title = a.attrs['title']
    body = getBody(hyperlink)
    date = getDate(hyperlink)
    print(title)
    print('\n')
    print(date)
    print('\n')
    print(clean(body) + '\n')
    #file.write(title)
    #file.write('\n')
    #file.write(date)
    #file.write('\n')
    #file.write(clean(body) + '\n')
file.close()

