import os
import sys
import urllib.request

client_id = "elPa0ixHaX_pjhOhA1Bw"  #클라이언트의 ID
client_secret = "l6CF6L7usB"        #클라이언트 PW

input_ = urllib.parse.quote(str(input("검색어를 입력하십시오: "))) #검색어를 인코딩
u_rl = 'https://openapi.naver.com/v1/search/' #API 게이트웨이 서버
target = 'news?'  #blog, news, book 등 검색 영역
display = '&display=100'#검색되는 데이터의 개수
query = '&query=' + input_
url = u_rl + target + display + query

file = open("C:\\Users\\JSW\\Downloads\\naver_news.txt", "a", encoding='utf-8')

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request)
rescode = response.getcode()

if(rescode==200): #HTTP 상태코드. 200은 정상 / 404는 존재x / 5xx는 서버에 문제가 있음
    response_body = response.read()
    print(response_body.decode('utf-8'))        #콘솔창에 출력
    file.write(response_body.decode('utf-8'))   #txt파일에 출력
    file.close()
else:
    print("Error Code:" + rescode)
    file.close()
