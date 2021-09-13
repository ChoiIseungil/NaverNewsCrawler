# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import time

#한글깨짐 방지
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
< naver 뉴스 검색시 리스트 크롤링하는 프로그램 > _select사용
- 크롤링 해오는 것 : 링크,제목,신문사,내용요약본
- 내용요약본  -> 정제 작업 필요
- 리스트 -> 딕셔너리 -> df -> 엑셀로 저장
'''''''''''''''''''''

#각 크롤링 결과 저장하기 위한 리스트 선언
title_text=[]
link_text=[]
date_text=[]
contents_text=[]
result={}

headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36" }
# headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"}
#엑셀로 저장하기 위한 변수
RESULT_PATH ='/Users/ChoiIseungil-ilb/Desktop/KAIST/2021 Fall/CS474 텍스트마이닝/Homeworks/results/'  #결과 저장할 경로


def clean_text(text):
    text = re.sub("[^가-힣a-z0-9\s]","", text)
    text = re.sub("[\(\[\【\〖\〔].*?[\)\]\】\〗\〕]", " ", text)
    return text

#내용 정제화 함수
def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<dl>.*?</a> </div> </dd> <dd>', '',str(contents)).strip()  #앞에 필요없는 부분 제거
    second_cleansing_contents = re.sub('<ul class="relation_lst">.*?</dd>', '', first_cleansing_contents).strip()#뒤에 필요없는 부분 제거 (새끼 기사)
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    # forth_cleansing_contents = clean_text(third_cleansing_contents)
    contents_text.append(third_cleansing_contents)

#크롤링 시작
def crawler(maxpage,query,sort,s_date,e_date):
    s_from = s_date.replace(".","")
    e_to = e_date.replace(".","")
    page = 1
    maxpage_t =(int(maxpage)-1)*10+1   # 11= 2페이지 21=3페이지 31=4페이지  ...81=9페이지 , 91=10페이지, 101=11페이지
    last_date = "2021.09.14"
    while page <= maxpage_t:
        url = "https://search.naver.com/search.naver?where=news&query=" + query + "&sort="+sort+"&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(page)
        response = requests.get(url,headers= headers,verify=False)
        # time.sleep(5)
        assert (response.status_code == 200)

        html = response.text

        #뷰티풀소프의 인자값 지정
        soup = BeautifulSoup(html, 'html.parser')

        atags = soup.find_all('a', 'news_tit')
        source_lists = soup.find_all('a', 'info press')
        # print(source_lists)
        date_lists = soup.find_all('div','info_group')
        # print(date_lists)
        title= ''
        contents_lists = soup.find_all('a','api_txt_lines dsc_txt_wrap')
        for atag, date_list, source_list, contents_list in zip(atags,date_lists,source_lists,contents_lists):
            if source_list.text != '동아일보': continue
            if title == atag.get('title'): break
            title = atag.get('title')
            last_date = date_list.find('span','info').text
            date_text.append(last_date)
            print(last_date)
            title_text.append(clean_text(title))     #제목
            link_text.append(atag['href'])   #링크주소
            contents_cleansing(contents_list) #본문요약 정제화


        #모든 리스트 딕셔너리형태로 저장
        result= {"title":title_text , "date":date_text ,"contents": contents_text ,"link":link_text }
        df = pd.DataFrame(result)  #df로 변환
        page += 10

    # 새로 만들 파일이름 지정
    outputFileName = '%s_%s-%s.csv' % (query, s_date, last_date)

    df.to_csv(RESULT_PATH+outputFileName)
    print("Total %d page crawled", maxpage_t)

#메인함수
def main():
    # info_main = input("="*50+"\n"+"입력 형식에 맞게 입력해주세요."+"\n"+" 시작하시려면 Enter를 눌러주세요."+"\n"+"="*50)
    maxpage = input("최대 크롤링할 페이지 수 입력하시오: ") #10,20...
    query = input("검색어 입력: ") #네이버, 부동산...
    # sort = input("뉴스 검색 방식 입력(관련도순=0  최신순=1  오래된순=2): ")    #관련도순=0  최신순=1  오래된순=2
    s_date = input("시작날짜 입력(2019.01.04):")  #2019.01.04
    # e_date = input("끝날짜 입력(2019.01.05):")   #2019.01.05

    # maxpage = "12000"
    # query = "강풍"
    sort = "2"
    # s_date = "2009.04.28"
    e_date = "2021.09.13"
    print("Crawling Start")
    print(query, s_date, e_date)
    crawler(maxpage,query,sort,s_date,e_date)
    print()
    print("Crawling Done")

#메인함수 수행
main()