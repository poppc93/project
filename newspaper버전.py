from urllib.request import urlopen
from newspaper import Article
from bs4 import BeautifulSoup
import re
from datetime import datetime

def getArticle(url):
    a = Article(url, language='ko')
    a.download()
    a.parse()

    return a
   
def clean(body): #기사 본문 내용에서 기사내용과 관련없는 내용을 정리한다
    spl = re.split('▶', body) # 기사가 끝날 때 '▶'문자와 함께 광고가 나오는데 그 광고의 앞부분만 가져옴
    cleaned = re.sub('[A-Za-z0-9\._+]+@[A-Za-z]+\.(co.kr|com|net)', '', spl[0]) #기자의 이메일 제거
    cleaned = re.sub('[\}\{\[\]\/?,:;|\)*~`!^\-+_<>@\#$%&\\\=\(\'\"]', '', cleaned) #기타 기호 제거
    return cleaned

def getArticleLinks(i):
    year = str(datetime.today().year)
    month = datetime.today().month
    if(month<10): #1월부터 9월이면 0x형태의 문자열로 입력
        month = '0' + str(month)
    else:
        month = str(month)
    date = datetime.today().day
    if(date<10): #1일부터 9일이면 0x형태의 문쟈열로 입력
        date = '0' + str(date)
    else:
        date = str(date)
    page = "#&date="+year+"-"+month+"-"+date+" 00:00:00&page=1" #현재날짜의 페이지 링크
    
    link = "http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=10"+str(i)+page
    html = urlopen(link) #기준이 되는 페이지는 네이버뉴스 경제 홈
    bs0bj = BeautifulSoup(html, "html.parser")
    links = bs0bj.find("div", {"class":"section_body"}).findAll("a")
    return links
    #기사의 본문으로 연결되는 하이퍼링크 반환

file = open("output.txt", 'w', -1,'utf-16')
for i in range(0, 3): #0=정치, 1=경제, 2=사회, 3=생활/문화 홈을 차례로 방문
    links = getArticleLinks(i)
    for a in links:
        try:
            hyperlink = a.attrs['href']
            article = getArticle(hyperlink)
            print(article.title+'\n')
            print(clean(article.text)+'\n')
   
          
    
          #  file.write(article.title+'\n')
          #  file.write(article.text+'\n')
        except UnicodeEncodeError as e: #유니코드 인코드 에러 발생시.
            print("Unicode Enconde Error")
       
file.close()

