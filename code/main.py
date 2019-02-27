# coding=utf-8
"""This project is devoloped to answer
the authorship question of Bible.
The processing pipeline is: epubreader ->
rangefreq -> stats -> textsplit -> featselect ->
featextract -> classifier -> evaluation
"""

import sys
import getopt
import re
import csv
import matplotlib.pyplot as plt
import numpy
import operator
import epubreader as er
import rangefreq as rf
import stats
import multiprocessing as mp


def usage():
    ## print the usage of command line tool
    print """
**************************************PGAUTHOR V1.0 Only For Bible************************************************
Example: python main.py -a 'god',1,1,1,100,100,100 -l 1000 -n 4 -s 0 -m 0 -f 1 -c 1
Each notion represents:
-h  help
-a  all the argument for this tool, including [nword,loc0,loc1]
    nword (string): any word or phrase;
    loc0,loc1 (list): the [BookID,ChapterID,VerseID] for origin and destination.
        a) if BookID exceeds the book number, it will process the whole Bible;
        b) if [ChapterID: VerseID] can not match the ones within the Book, it will process the whole book.
        c) note that there are no space between commas
-l  chunk length (integer or string), number: word number, 'book': the whole book [default: 1000, maximum: 100000]
-n  ngram (integer): the maximum length of a phrase, [default: 4, maximum: 10]
-s  case (integer), 0: not case-sensitive, 1: case sensitive , [default: 1]
* -m  ngram method, 0: word-ngram, 1: character-ngram [default: 0]
* -f  feature selection algorithm, 0: freq-based, 1: even-uneven-freq based [default: 1]
* -c  classifier, 0: naive bayes, 1: SVM [default: 0]
******************************************************************************************************************
"""


def main(argv):
    ## This contains the whole process and pipeline of this project
    ## deal with the inputs
    try:
        opts, args = getopt.getopt(argv, "a:l:n:s:m:f:c:h")
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    ## set default values
    leng = 1000
    ngram = 4
    case = 1
    ngram_m = 0
    feat_m = 0
    clas_m = 0

    ## handle the options
    # try:
    for opt_name, opt_value in opts:
        if opt_name == "-a":
            values = opt_value.split(',')
            for i in range(1,7):
                values[i] = int(values[i])
            nword = values[0]
            loclist0 = values[1:4]
            loclist1 = values[4:]
        elif opt_name == "-l":
            leng = int(opt_value)
            if leng > 100000 or leng <= 0:
                raise Exception('CommandError: check the range of -l')
        elif opt_name == "-n":
            ngram = int(opt_value)
            if ngram > 10 or ngram <= 0:
                raise Exception('CommandError: check the range of -n')
        elif opt_name == "-s":
            case = int(opt_value)
            if case not in (0, 1):
                raise Exception('CommandError: check the range of -s')
        elif opt_name == "-m":
            ngram_m = int(opt_value)
            if ngram_m not in (0, 1):
                raise Exception('CommandError: check the range of -m')
        elif opt_name == "-f":
            feat_m = int(opt_value)
            if feat_m not in (0, 1):
                raise Exception('CommandError: check the range of -f')
        elif opt_name == "-c":
            clas_m = int(opt_value)
            if clas_m not in (0, 1):
                raise Exception('CommandError: check the range of -c')
        elif opt_name == "-h":
            usage()
            sys.exit()
        else:
            raise Exception('CommandError: check the notion of args')
    # except:
    #     print 'CommandError: check the range of args'
    #     usage()
    #     sys.exit()

    ## first question
    rf.word_phrase_freq(nword, loclist0, loclist1, case, leng)
    ## second question
    stats.rank_writer('book', ngram)
    plt.show()

if __name__ == "__main__":
    main(sys.argv[1:])
