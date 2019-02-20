import re
import csv
import matplotlib.pyplot as plt
import numpy
import operator
import epubreader as er
import rangefreq as rf
import multiprocessing as mp


def comp_vari(freqlist):
    ## Compute coefficient of variation
    freqnp = numpy.array(freqlist)
    if numpy.mean(freqnp) == 0:
        return 0
    else:
        return numpy.std(freqnp) / numpy.mean(freqnp)


def even_word(leng):
    ## get ten most evenly distributed words and variated ones
    loc0 = er.Location([1, 1, 1])
    loc1 = er.Location([100, 100, 100])

    text = er.get_range_text(er.filenum, loc0, loc1)[0]
    count = rf.word_count(text)
    ## cut texts into chunks of length leng
    textarr = rf.cut_text(text, leng)
    freqs, freqsarr = rf.all_word_freq(textarr, count, leng)

    wordstd = dict()
    for word in freqs.keys():
        wordstd[word] = comp_vari(rf.word_freq(word, freqsarr))
    rank_word = sorted(wordstd.items(), key = operator.itemgetter(1), reverse = False)

    return rank_word


def even_nword(leng):
    ## get ten most evenly distributed words and variated ones
    ngram = 6
    loc0 = er.Location([1, 1, 1])
    loc1 = er.Location([100, 100, 100])

    text, punc_text = er.get_range_text(er.filenum, loc0, loc1)
    count = rf.word_count(text)
    ## cut texts into chunks of length leng

    nwordcv = dict()
    nwordcv0 = dict()
    nwordcv1 = dict()
    ## compute coefficient of variation based on book or word numbers
    if leng == 'book':
        leng = 1000
        textarr = rf.cut_text(text, leng)
        freqs, freqsarr0, freqsarr1 = rf.all_nword_freq(textarr, text, punc_text, ngram, leng)
        freqsarr = rf.all_nword_freq_book(freqs, ngram)
        for nword in freqs.keys():
            nwordcv[nword] = comp_vari(rf.word_freq(nword, freqsarr))
    else:
        textarr = rf.cut_text(text, leng)
        freqs, freqsarr0, freqsarr1 = rf.all_nword_freq(textarr, text, punc_text, ngram, leng)
        for nword in freqs.keys():
            nwordcv0[nword] = comp_vari(rf.word_freq(nword, freqsarr0))
            nwordcv1[nword] = comp_vari(rf.word_freq(nword, freqsarr1))

    rank_nword = sorted(nwordcv.items(), key = operator.itemgetter(1), reverse = False)
    rank_nword0 = sorted(nwordcv0.items(), key = operator.itemgetter(1), reverse = False)
    rank_nword1 = sorted(nwordcv1.items(), key = operator.itemgetter(1), reverse = False)

    return rank_nword, rank_nword0, rank_nword1


def csv_writer(ranks, csvfile):
    ## write csv into an opened file, return top_even and top_uneven
    rankwriter = csv.writer(csvfile, delimiter=',')
    top_even = []
    top_uneven = []
    num = 0

    print '\nTop 25 word or phrase that are evenly distributed:'
    for rank in ranks:
        if rank[1]:
            num += 1
            nword = str(rank[0])
            top_even.append(nword)
            print nword
            if num > 25:
                break

    print '\nTop 25 word or phrase that are unevenly distributed:'
    for rank in ranks[-25: ]:
        nword = str(rank[0])
        top_uneven.append(nword)
        print nword

    for rank in ranks:
        if rank[1]:
            rankwriter.writerow([str(rank[0]), rank[1]])

    return top_even, top_uneven


def rank_writer(leng):
    ## leng can either be word number or string 'book'
    ranks, ranks0, ranks1 = even_nword(leng)
    if any(ranks):
        with open('../doc/rank_nword/rank_nword_' + str(leng) + '.csv', 'wb') as csvfile:
            csv_writer(ranks, csvfile)
    if any(ranks0):
        with open('../doc/rank0_nword/rank0_nword_' + str(leng) + '.csv', 'wb') as csvfile:
            csv_writer(ranks0, csvfile)
    if any(ranks1):
        with open('../doc/rank1_nword/rank1_nword_' + str(leng) + '.csv', 'wb') as csvfile:
            csv_writer(ranks1, csvfile)
    return


def multicore_rank_writer(core, leng):
    ## run faster using multiprocessing on multicores of CPU
    pool = mp.Pool(processes = core)
    pool.map(rank_writer, leng)
    return


if __name__ == "__main__":
    # multicore_rank_writer(6, numpy.arange(1000,11000,1000))
    rank_writer('book')
