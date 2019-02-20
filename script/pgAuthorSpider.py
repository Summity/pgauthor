#-*- coding: UTF-8 -*-

import sys
import time
import re
import urllib
#import urllib2
import requests
import numpy as np
from bs4 import BeautifulSoup
#from openpyxl import Workbook

#reload(sys)
#sys.setdefaultencoding('utf8')

#Some User Agents
hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
{'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
{'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]


#get top 100 authors of today/last 7days/last 30 days
def author_spider(author_tag):
    url = 'https://www.gutenberg.org/browse/scores/top#' + author_tag
    time.sleep(np.random.rand() * 5)

    source_code = requests.get(url)
    plain_text = source_code.text

    cast_text = plain_text[plain_text.index('<h2 id="authors-last30">Top 100 Authors last 30 days</h2>'):]
    print(cast_text)

    soup = BeautifulSoup(cast_text, "lxml")

    name = [list.text for list in soup.find_all('li')]
    link = [a['href'] for a in soup.find_all('a', href=True) if a.text]

    for all in link:
        print(all)
        book_url = 'https://www.gutenberg.org' + all
        book_source = requests.get(book_url)
        book_text = book_source.text

        book_soup = BeautifulSoup(book_text, 'lxml')
        author_index = str(book_soup.find_all("a",{"name": all[18: ]})).lstrip('[').rstrip(']')
        #author_index = '<h2>'+ author_index + ' <a href=\"' +all[17: ]+ '\" title=\"Link to this author\">¶</a></h2>'
        author_index = author_index + ' <a href=\"' + all[17:] + '\" title=\"Link to this author\">¶</a>'
        print(book_soup.find("h2", text=author_index))
        print(book_soup.find("h2", text=author_index).find_next_siblings("a"))
        book_cast_text = book_text[book_text.index(author_index)]
        #print(book_text.index(author_index))
        #print(book_soup.find_next_siblings("a"))

        book_cast_soup = BeautifulSoup(book_cast_text, 'lxml')
        book_name = [list.text for list in book_cast_soup.find_all('li', class_="pgdbetext")]
        book_link = [a['href'] for a in book_cast_soup.find_all('a', href=True) if a.text] #still got problem here, compatible with others

        print(book_link)
    return 0

if __name__=='__main__':
    author_spider('authors-last30')