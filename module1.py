from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import datetime

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
            title = a.attrs['title']
            article = getArticle(hyperlink)
            #print(title)
            #print(article[1])
            #print(clean(article[0]) + '\n\n')
    
            file.write(title+'\n')
            file.write(article[1]+'\n')
            file.write(clean(article[0])+'\n')
        except UnicodeEncodeError as e: #유니코드 인코드 에러 발생시.
            print("Unicode Enconde Error")
       
file.close()

