from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def getArticle(url):
    html = urlopen(url)
    bs0bj = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    article = ['', '']
    for item in bs0bj.find_all('div', id='articleBodyContents'):#기사의 본문이 있는 태그를 찾음
        article[0] = article[0] + str(item.find_all(text=True))
        
    item = bs0bj.find_all('span', {'class':'t11'})              #기사의 날짜가 있는 태그를 찾음
    article[1] = article[1] + str(item[0].find_all(text=True))  #첫번째 span태그만을 가져와서 text파일을 가져옴 ->즉 기사의 최초 작성 시기를 가져온다.
    article[1] = re.sub('[\-:]', ' ', article[1])               # : 과 - 를 공백으로 대체
    article[1] = re.sub('[\'\[\]]', '', article[1])             # '과 대괄호 제거

    return article
    #article[0]:본문
    #artilce[1]:날짜 (반환되는 형식은 년 월 일 시 분 초. ex) 2017 11 03 10 18 34)

def clean(body): #기사 본문 내용에서 기사내용과 관련없는 내용을 정리한다
    spl = re.split('▶', body) # 기사가 끝날 때 '▶'문자와 함께 광고가 나오는데 그 광고의 앞부분만 가져옴
    cleaned = re.sub('[A-Za-z0-9\._+]+@[A-Za-z]+\.(co.kr|com|net)', '', spl[0]) #기자의 이메일 제거
    cleaned = re.sub('[\}\{\[\]\/?.,:;|\)*~`!^\-+_<>@\#$%&\\\=\(\'\"]', '', cleaned) #기타 기호 제거
    cleaned = re.sub('tnt', ' ', cleaned)
    spl2 = re.split('Callback n n ', cleaned) #기사와 관련없는 문자 제거
    return spl2[1]

def getArticleLinks(page):
    html = urlopen("http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=101"+page) #기준이 되는 페이지는 네이버뉴스 경제 홈
    bs0bj = BeautifulSoup(html, "html.parser")
    return bs0bj.find("div", {"class":"section_body"}).findAll("a", href=re.compile("^(http://news.naver.com/main/read)"))
    #기사의 본문으로 연결되는 하이퍼링크 반환

def getPageLink(i):
    year = "2017"
    month = "11"
    date = "02"
    page = "#&date="+year+"-"+month+"-"+date+" 00:00:00&page="+ str(i)
    return page #기사 홈에서 페이지링크를 가져온다

file = open("output.txt", 'a', -1,'utf-16')
for i in range(1, 5):
    page = getPageLink(i)
    links = getArticleLinks(page)
    for a in links:
        try:
            hyperlink = a.attrs['href']
            title = a.attrs['title']
            article = getArticle(hyperlink)
            #print(title)
            #print(article[1])
            #print(clean(article[0]) + '\n\n')
    
            file.write(title+'\n')
            file.write(article[1]+'\n')
            file.write(clean(article[0])+'\n')
        except UnicodeEncodeError as e:
            print("Unicode Enconde Error")
       
file.close()

