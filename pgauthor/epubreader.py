import zipfile
import urllib
import re
import string
import numpy as np
from bs4 import BeautifulSoup

## global filename strings
filenum = '10'
htmlreq = "@public@vhost@g@gutenberg@html@files@" + filenum + "@" + filenum + "-h@"+ filenum +"-h-"
content = urllib.urlopen("../book/pg" + filenum + "/OEBPS/" + htmlreq + "0.htm.html").read()

class Location:
    """class for Location within books"""
    def __init__(self, loclist):
        self.loclist = loclist

    def get_info(self, htmlreq, content, flag):
        soup = BeautifulSoup(content, "lxml")
        ## deal with the lastpage issue
        if self.loclist[0] > 65:
            self.loclist[0] = 66
            self.lastpage = 1
        else:
            self.lastpage = 0

        if flag == 0 or self.lastpage == 1:
            url = soup.find_all('a', class_ = 'c2 pginternal')[self.loclist[0]].get('href').split('#')
        else:
            url = soup.find_all('a', class_ = 'c2 pginternal')[self.loclist[0] + 1].get('href').split('#')

        self.link = url[0]
        self.bookname = url[1]
        self.pagenum = int(self.link.split(htmlreq)[1].split('.htm')[0])


def unzip_file(filenum):
    ## unzip requested books
    zip_ref = zipfile.ZipFile('../book/pg' + filenum + '.epub', 'r')
    zip_ref.extractall('../book/pg' + filenum)
    zip_ref.close()
    return


def get_page_text(filenum, htmlreq, pagenum):
    ## get all text on a single page
    allpage = urllib.urlopen("../book/pg" + filenum + "/OEBPS/" + htmlreq + str(pagenum) + ".htm.html").read()
    soup = BeautifulSoup(allpage, "lxml")
    if pagenum == 0:
        page_text = soup.find_all('p')
    else:
        page_text = soup.find_all('body')
    return page_text


def check_range(loc0, loc1):
    ## compare the origin and destination
    if loc0.loclist[0] > loc1.loclist[0]:
        raise Exception("LocationError: the BookID of your origin is greater than that of the destination.")
    elif loc0.loclist[1] > loc1.loclist[1]:
        raise Exception("LocationError: the ChapterID of your origin is greater than that of the destination.")
    elif loc0.loclist[2] > loc1.loclist[2]:
        raise Exception("LocationError: the VerseID of your origin is greater than that of the destination.")


def book_name(bookname):
    ## get book name which is seperated by space
    bookname = ' '.join(bookname.split('_'))
    if bookname.find('Moses') != -1:
        parts = bookname.split('Moses')
        bookname = parts[0] + 'Moses:' +parts[1]
    return bookname


def trim_rest_text(rest_text, page_text, loc0, loc1):
    ## get trimmed rest_text without html formats
    textstr = re.sub( r'<.*?>', '', str(page_text))

    if loc0.pagenum == loc1.pagenum and loc1.lastpage == 0: # deal with same page ones
        textstr_trim = textstr.split(book_name(loc0.bookname))[1].rsplit(book_name(loc1.bookname))[0]
        rest_text = textstr_trim.replace('\n', '')
    else:
        if str(page_text).find(loc0.bookname) != -1:
            textstr_trim = str(textstr).split(book_name(loc0.bookname))[1]
        if str(page_text).find(loc1.bookname) != -1:
            textstr_trim = str(textstr).rsplit(book_name(loc1.bookname))[0]
        if str(page_text).find(loc0.bookname) == -1 & str(page_text).find(loc1.bookname) == -1:
            textstr_trim = textstr
        textstr_trim = unicode(textstr_trim, 'utf-8')
        rest_text = rest_text + textstr_trim.replace('\n', '')
    return rest_text


def books_text(all_text, loc0, loc1):
    ## get all text within the BookID range
    ## need to consider the first and last page, and loctions which are on the same page
    rest_text = u''

    if loc1.lastpage == 1:
        for page_text in all_text[0 : -1]:
            rest_text = trim_rest_text(rest_text, page_text, loc0, loc1)

        ## add last page to rest_text whose loc BookID is 66
        textstr = str(all_text[-2]).rsplit('</h3>', 1)[1] + str(all_text[-1]).rsplit('<div', 1)[0]
        textstr_trim = re.sub( r'<.*?>', '', textstr)
        rest_text = rest_text + textstr_trim.replace('\n', '')
    else:
        for page_text in all_text:
            rest_text = trim_rest_text(rest_text, page_text, loc0, loc1)

    return rest_text

def book_text(all_text, bookid):
    ## get all text within the one book
    loc0 = Location([bookid, 1, 1])
    loc1 = Location([bookid, 100, 100])

    ## get book infos within the range
    loc0.get_info(htmlreq, content, 0)
    loc1.get_info(htmlreq, content, 1)

    return books_text(all_text, loc0, loc1)


def get_range_text(filenum, loc0, loc1):
    ## get the text within [loc0, loc1]
    try:
        check_range(loc0, loc1)
    except:
        print 'LocationError: your origin is greater than the destination.'
        return

    ## get book infos within the range
    loc0.get_info(htmlreq, content, 0)
    loc1.get_info(htmlreq, content, 1)

    ## get all text within the BookID range
    all_text = []
    if loc1.lastpage == 0:
        for page in range(loc0.pagenum, loc1.pagenum + 1):
            all_text = all_text + get_page_text(filenum, htmlreq, page)
    else:
        for page in range(loc0.pagenum, 67):
            all_text = all_text + get_page_text(filenum, htmlreq, page)

    rest_text = books_text(all_text, loc0, loc1)

    ## get range_text by the ChapterID and VerseID
    ## If loc1 surpasses the Maximum ChapterID or BookID, it will return an exception
    ## If loc2 surpasses the Maximum ChapterID or BookID, it will return all text till the end.
    strloc0 = str(loc0.loclist[1]) + ':' + str(loc0.loclist[2])
    strloc1 = str(loc1.loclist[1]) + ':' + str(loc1.loclist[2] + 1)

    if loc1.loclist[0] > 65:
        print 'Warning: the BookID is out of range, will include all words to the end of Bible.'

    try:
        if book_text(all_text, loc0.loclist[0]).find(strloc0) == -1:
            raise Exception("LocationError: origin has no verse of [ChapterID: VerseID].")
        elif book_text(all_text, loc1.loclist[0]).find(strloc1) == -1:
            # print "Warning: the [ChapterID, VerseID] of destination is out of range, will get the whole book."
            pass
    except:
        print 'LocationError: origin has no verse of [ChapterID: VerseID], please specify it again.'
        return

    try:
        raw_range_text = rest_text.split(strloc0, 1)[1].rsplit(strloc1, 1)[0]
        punc_range_text = re.sub( r'[0-9]*:[0-9]*\s', ' ', raw_range_text)
        plain_range_text = re.sub(r'[^\w\s]', '', punc_range_text)
    except:
        print 'LocationError: origin is out of range, please specify it again.'
        return

    return plain_range_text, punc_range_text


if __name__ == "__main__":
    #unzip_file(filenum)

    # for bookid in range(1, 67):
    #     try:
    #         loc0 = Location([bookid, 1, 1]) ## should deal with the range issue
    #         loc1 = Location([bookid, 100, 100])
    #         get_range_text(filenum, loc0, loc1)
    #     except:
    #         print bookid, loc0.bookname, loc1.bookname, loc0.pagenum, loc1.pagenum

    ## loc = [BookID, ChapterID, VerseID]
    loc0 = Location([1, 1, 1]) ## should deal with the range issue
    loc1 = Location([1, 1, 3])

    plain_range_text, punc_range_text = get_range_text(filenum, loc0, loc1)
