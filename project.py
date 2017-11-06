from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
from konlpy.tag import Kkma
from konlpy.tag import Twitter
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import codecs
import subprocess
import os
import re

def getArticle(url):
    html = urlopen(url)
    bs0bj = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    article = ['', '']
    for item in bs0bj.find_all('div', id='articleBodyContents'):#기사의 본문이 있는 태그를 찾음
        article[0] = article[0] + str(item.find_all(text=True))
        
    #item = bs0bj.find_all('span', {'class':'t11'})              #기사의 날짜가 있는 태그를 찾음
    #article[1] = article[1] + str(item[0].find_all(text=True))  #첫번째 span태그만을 가져와서 text파일을 가져옴 ->즉 기사의 최초 작성 시기를 가져온다.
    #article[1] = re.sub('[\-:]', ' ', article[1])               # : 과 - 를 공백으로 대체
    #article[1] = re.sub('[\'\[\]]', '', article[1])             # '과 대괄호 제거

    return article
    #article[0]:본문
    #artilce[1]:날짜 (반환되는 형식은 년 월 일 시 분 초. ex) 2017 11 03 10 18 34)

def clean(body): #기사 본문 내용에서 기사내용과 관련없는 내용을 정리한다
    spl = re.split('▶', body) # 기사가 끝날 때 '▶'문자와 함께 광고가 나오는데 그 광고의 앞부분만 가져옴
    cleaned = re.sub('[A-Za-z0-9\._+]+@[A-Za-z]+\.(co.kr|com|net)', '', spl[0]) #기자의 이메일 제거
    cleaned = re.sub('[\}\{\[\]\/?,:;|\)*~`!^\-+_<>@\#$%&\\\=\(\'\"]', '', cleaned) #기타 기호 제거
    cleaned = re.sub('기자', '기.', cleaned) # '000 기자'가 나오는 경우 .으로 문장 나눔
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

class SentenceTokenizer(object):
  def __init__(self):
    self.kkma = Kkma()
    self.twitter = Twitter()
    self.stopwords = ['무단전재', '세계일보', '바로가기', '국민일보', '기자', '를', '본문']
    #불용문자

  def t2s(self, text):
    sentences = self.kkma.sentences(text) #텍스트에서 문장 추출
    for idx in range(0, len(sentences)):
      if len(sentences[idx]) <= 10:
        sentences[idx-1] += (' '+sentences[idx])
        sentences[idx] = ''
    return sentences

  def get_nouns(self, sentences): #명사추출하기
    nouns = []
    for s in sentences:
      if s is not '':
        nouns.append(''.join([noun for noun in self.twitter.nouns(str(s)) if noun not in self.stopwords and len(noun)>1]))
    return nouns

class GraphMatrix(object):
  def __init__(self):
    self.tfidf = TfidfVectorizer()
    self.cnt_vec = CountVectorizer()
    self.graph_sentence = []

  def build_sent_graph(self, sentence):
    tf_idf_matrix = self.tfidf.fit_transform(sentence).toarray()
    self.graph_sentence = np.dot(tf_idf_matrix, tf_idf_matrix.T)
    return self.graph_sentence

  def build_words_graph(self, sentence):
    cnt_vec_mat = normalize(self.cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
    vocab = self.cnt_vec.vocabulary_
    return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word]:word for word in vocab}

class Rank(object):
  def get_ranks(self, graph, d=0.8):  # d : 현재 페이지에 만족하지 않고 다른 페이지로 이동할 확률
    A=graph
    matrix_size = A.shape[0]
    for id in range(matrix_size):
      A[id,id] = 0
      link_sum = np.sum(A[:,id])
      if link_sum != 0:
        A[:,id] /= link_sum
      A[:, id] *= -d
      A[id, id] = 1

    B = (1-d) * np.ones((matrix_size,1))
    ranks = np.linalg.solve(A, B)
    return {idx:r[0] for idx, r in enumerate(ranks)}

class TextRank(object):
  def __init__(self, text):
    self.sent_tokenize = SentenceTokenizer()
    self.sentences = self.sent_tokenize.t2s(text)
    self.nouns = self.sent_tokenize.get_nouns(self.sentences)
    self.graph_matrix = GraphMatrix()
    self.sent_graph = self.graph_matrix.build_sent_graph(self.nouns)
    self.words_graph, self.idx2word = self.graph_matrix.build_words_graph(self.nouns)
    self.rank = Rank()
    self.sent_rank_idx = self.rank.get_ranks(self.sent_graph)
    self.sorted_sent_rank_idx = sorted(self.sent_rank_idx, key=lambda k:self.sent_rank_idx[k], reverse=True)

  def summarize(self, sent_num=3): #최대 3개의 문장을 요약하여 리턴
    s=[]
    index=[]
    for i in self.sorted_sent_rank_idx[:sent_num]:
      index.append(i)
    index.sort()
    for i in index:
      s.append(self.sentences[i])
    return s

file = open("output.txt", 'w', -1,'utf-8')
for i in range(0, 4): #0=정치, 1=경제, 2=사회, 3=생활/문화 홈을 차례로 방문
    links = getArticleLinks(i) #분야당 25개의 기사 하이퍼링크를 가져온다
    for a in links:
        try:
            hyperlink = a.attrs['href']
            title = a.attrs['title']
            article = getArticle(hyperlink)
            #print(title)
            #print(article[1])
            #print(clean(article[0]) + '\n\n')
    
            file.write(title+'\t')
            #file.write(article[1]+'\n')
            file.write(clean(article[0])+'\n')
        except UnicodeEncodeError as e: #유니코드 인코드 에러 발생시.
            print("Unicode Enconde Error")
       
file.close()

command = 'Rscript'
args = os.getcwd()
path2script = args+'/lsa.R'

cmd = [command, path2script] #+ args

subprocess.check_output(cmd, universal_newlines=True)

for i in range(1, 4):
  file = codecs.open("topic "+str(i)+" .txt", "r", "utf-8")
  title = file.readline()
  body = file.readline()
  print("제목 : "+title)
  textrank = TextRank(body)
  j=1
  for row in textrank.summarize(3):
    print("요약 "+str(j)+" : "+row)
    j=j+1
  print()
  file.close()

