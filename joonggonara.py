from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import pyperclip
import time
from bs4 import BeautifulSoup

browser = webdriver.Chrome() # 현재파일과 동일한 경로일 경우 생략 가능

user_id = ''
user_pw = ''

# 1. 네이버 이동
browser.get('https://www.naver.com')

# 2. 로그인 버튼 클릭
elem = browser.find_element_by_class_name('link_login')
elem.click()

# 3. id 복사 붙여넣기
elem_id = browser.find_element_by_id('id')
elem_id.click()
pyperclip.copy(user_id)
elem_id.send_keys(Keys.CONTROL, 'v')
time.sleep(1)

# 4. pw 복사 붙여넣기
elem_pw = browser.find_element_by_id('pw')
elem_pw.click()
pyperclip.copy(user_pw)
elem_pw.send_keys(Keys.CONTROL, 'v')
time.sleep(1)

# 5. 로그인 버튼 클릭
browser.find_element_by_id('log.login').click()

time.sleep(2)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import re
article_id_regex = re.compile('articleid=[0-9]+')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search/{search_keyword}")
@app.post("/search")
def get_items(search_keyword: str):
    ## 중고나라 이동
    browser.get('https://cafe.naver.com/joonggonara')

    queryInput = browser.find_element_by_id('topLayerQueryInput')
    queryInput.click()
    pyperclip.copy(search_keyword)
    queryInput.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    queryInput.send_keys(Keys.ENTER)
    innerHtml = browser.find_element_by_id('cafe_main')
    browser.switch_to.frame(innerHtml)

    documents = []

    ## 게시글 크롤링
    for i in range(1, 10):
        # time.sleep(2)

        html = browser.page_source
        soupCB = BeautifulSoup(html, 'html.parser')
        board = soupCB.select('.article-board')[1]
        items = board.select('tr')
        for item in items:
            level_src = item.select('td.td_name .mem-level > img')[0]['src']
            if level_src == 'https://cafe.pstatic.net/levelicon/1/1_150.gif':
                continue

            title = item.select('td.td_article a.article')
            if len(title) <= 0:
                continue
            title = title[0].text.strip()

            href = item.find("a",{"class":"article"}).get("href")
            article_id = int(article_id_regex.search(href).group().strip().strip('articleid='))

            documents.append({
                "title": title,
                "article_id": article_id
            })

        atags = browser.find_elements_by_css_selector('.prev-next > a')
        atags[i].send_keys(Keys.ENTER)

    browser.switch_to.default_content()

    return documents


@app.get("/item/{article_id}")
def read_item(article_id: int):
    browser.get('https://cafe.naver.com/joonggonara?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D10050146%2526page%3D1%2526boardtype%3DL%2526articleid%3D'+str(article_id)+'%2526referrerAllArticles%3Dtrue')
    innerHtml = browser.find_element_by_id('cafe_main')
    browser.switch_to.frame(innerHtml)
    time.sleep(1)

    html = browser.page_source
    print(html)
    soupCB = BeautifulSoup(html, 'html.parser')
    cost = soupCB.select('.ProductPrice')
    if len(cost) < 1:
        cost = -1
    else:
        cost = cost[0].text.strip()

    title = soupCB.select('.ProductName')
    if len(title) <= 0:
        title = ""
    else:
        title = title[0].text.strip()

    return {"article_id": article_id, "title":title, "cost": cost}


#6. html 정보 출력
print(browser.page_source)

#7. 브라우저 종료
browser.close() # 현재 탭만 종료
browser.quit() # 전체 브라우저 종료
