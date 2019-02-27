import re
import matplotlib.pyplot as plt
import epubreader as er


def word_count(text):
    ## count words of any text input
    return len([word for word in text.split() if word.isalpha()])


def cut_text(text, leng):
    ## cut text into chunks of words in length leng, return an array of texts
    count = word_count(text)
    num = 0 # count words from 0 to count
    chunk = ''
    textarr = [ ]
    for word in text.split():
        if word.isalpha():
            num += 1
            chunk = chunk + ' ' + word
            if num % leng != 0:
                if num == count:
                    textarr.append(chunk)
            else:
                textarr.append(str(chunk))
                chunk = ''
    return textarr


def all_word_freq(textarr, count, leng):
    ## check the freq for all words
    ## freqs represents word freqs for the whole range
    ## freqsarr represents an array of freqs within ranges
    freqs = dict()
    chunkfreqs = dict()
    freqsarr = []
    num = 0

    for chunk in textarr:
        words = chunk.split()
        for word in words:
            num += 1
            ## word freqs for the whole range
            if word in freqs:
                freqs[word] += 1.0 / count
            else:
                freqs[word] = 1.0 / count
            ## an array of freqs within ranges
            if word in chunkfreqs:
                chunkfreqs[word] += 1.0 / leng
            else:
                chunkfreqs[word] = 1.0 / leng
            if num % leng !=0:
                if num == count:
                    freqsarr.append(chunkfreqs)
            else:
                freqsarr.append(chunkfreqs)
                chunkfreqs = dict()
    return freqs, freqsarr


def all_nword_freq(textarr, text, punc_text, ngram, leng):
    ## check the freq for all words / phrases (consider punctuations)
    ## freqs represents word freqs for the whole range
    ## freqsarr represents an array of freqs within ranges
    nword_counts = dict()  # count appearance of each word / phrase
    nword_count = [0]*ngram   # count total times of appearence of each phrase length
    freqs = dict()
    freqsarr0 = []
    freqsarr1 = []
    word_count = 0
    chunkfreqs = dict()

    sentences = re.compile('[^\w\s]').split(punc_text)

    ## get all words / phrases
    ## First way: phrases are gained out of sentences between punctuantions
    ## devide approximate length (word_count is max leng + ngram)
    for sentence in sentences:
        words = sentence.split()
        word_count += len(words)
        if word_count / leng == 0:
            sent_len = len(words)
            phra_len = sent_len if sent_len <= ngram else ngram
            for m in range(0, phra_len):
                for n in range(0, sent_len):
                    if n + m <= sent_len:
                        nword_count[m] += 1
                        nword = str(' '.join(words[n: n + m]))
                        if nword in nword_counts:
                            nword_counts[nword] += 1
                        else:
                            nword_counts[nword] = 1
                        if nword in chunkfreqs:
                            chunkfreqs[nword] += 1.0
                        else:
                            chunkfreqs[nword] = 1.0
        else:
            for nword in chunkfreqs:
                chunkfreqs[nword] = chunkfreqs[nword] / word_count
            freqsarr0.append(chunkfreqs)
            chunkfreqs = dict()
            word_count = 0

    ## freqs of each word or phrase in the whole range
    for nword in nword_counts.keys():
        amount = nword_count[len(nword.split()) - 1]
        freqs[nword] = float(nword_counts[nword]) / amount

    ## Second way: phrases are gained in chunks, devide the exact chunk length
    ## However, without punctuations. Some words may be joined and some phrases may be separated by chunks
    ## Words between books can be joined together
    for chunk in textarr:
        words = chunk.split()
        chunkfreqs = dict()
        for m in range(0, leng):
            for n in range(0, ngram):
                if m + n <= leng:
                    nword = str(' '.join(words[m: m + n]))
                    if nword_counts.has_key(nword):
                        if nword in chunkfreqs:
                            chunkfreqs[nword] += 1.0 / leng
                        else:
                            chunkfreqs[nword] = 1.0 / leng

        freqsarr1.append(chunkfreqs)

    return freqs, freqsarr0, freqsarr1


def plotfreq(nword, freqlist, leng):
    ## plot frequecny map for this word
    plt.plot(range(0, len(freqlist)), freqlist, 'g')
    plt.gca().set_xlim(-1, len(freqlist))
    plt.xlabel('Range(' + str(leng) + ' words)')
    plt.ylabel('Frequency')
    plt.title('Frequency Map of \"' + nword + '\" in Bible')
    return


def word_freq(nword, freqsarr):
    ## specify a single word and return the frequency of it and plot it
    ## This function is case sensitive
    freqlist = []
    for each in freqsarr:
        if each.has_key(nword):
            freqlist.append(each[nword])
        else:
            freqlist.append(0)
    return freqlist


def nword_freq(nword, textarr, leng):
    ## specify a word or phrase and return the frequency of it and plot it
    ## This function is case sensitive
    freqlist = []
    for text in textarr:
        freqlist.append(float(len(re.findall(nword, text))) / leng)
    plotfreq(nword, freqlist, leng)
    return freqlist


def nword_freq_no_case(nword, textarr, leng):
    ## specify a word or phrase and return the frequency of it and plot it
    ## This function is NOT case sensitive
    freqlist = []
    for text in textarr:
        freqlist.append(float(len(re.findall('(?i)' + nword, text))) / leng)
    plotfreq(nword, freqlist, leng)
    return freqlist


def word_phrase_freq(wp, loclist0, loclist1, flag, leng):
    ## a single function which can compute the whole thing
    ## if flag == 0, case insensitive; if flag == 1, case sensitive
    loc0 = er.Location(loclist0)
    loc1 = er.Location(loclist1)

    # text = er.get_range_text(er.filenum, loc0, loc1)[0]
    text, punc_text = er.get_range_text(er.filenum, loc0, loc1)
    count = word_count(text)
    ## cut texts into chunks of length leng
    textarr = cut_text(text, leng)
    # freqs, freqsarr = all_word_freq(textarr, count, leng)

    ## return freqlist based on the casing of words
    if flag:
        freqlist = nword_freq(wp, textarr, leng)
    else:
        freqlist = nword_freq_no_case(wp, textarr, leng)

    ## show the plot if you want
    # plt.show()
    return freqlist


def nword_freq_book(wp, flag):
    ## This function tries to find the freq of a word or phrase within a book
    ## freqlist[bookid]is the freq for one single book
    ## if flag == 0, case insensitive; if flag == 1, case sensitive
    freqlist = []

    for bookid in range(1, 67):
        loc0 = er.Location([bookid, 1, 1])
        loc1 = er.Location([bookid, 100, 100])
        text = er.get_range_text(er.filenum, loc0, loc1)[0]
        count = word_count(text)
        if flag:
            freqlist.append(float(len(re.findall(wp, text))) / count)
        else:
            freqlist.append(float(len(re.findall('(?i)' + wp, text))) / count)
    return freqlist


def all_nword_freq_book(freqs, ngram):
    ## This function tries to find the freq of a word or phrase within a book
    ## freqlist[bookid]is the freq for one single book
    ## if flag == 0, case insensitive; if flag == 1, case sensitive
    freqlist = []
    all_text = []
    freqsarr = []
    count = [0]*66

    for bookid in range(1, 67):
        loc0 = er.Location([bookid, 1, 1])
        loc1 = er.Location([bookid, 100, 100])
        all_text.append(er.get_range_text(er.filenum, loc0, loc1)[0])
        count[bookid - 1] = word_count(all_text[-1])

    bookid = 0
    for chunk in all_text:
        words = chunk.split()
        leng = len(words)
        chunkfreqs = dict()
        for m in range(0, len(words)):
            for n in range(0, ngram):
                if m + n <= leng:
                    nword = str(' '.join(words[m: m + n]))
                    if freqs.has_key(nword):
                        if nword in chunkfreqs:
                            chunkfreqs[nword] += 1.0 / count[bookid]
                        else:
                            chunkfreqs[nword] = 1.0 / count[bookid]
        bookid += 1
        freqsarr.append(chunkfreqs)
    return freqsarr

if __name__ == "__main__":
    #unzip_file(er.filenum)

    ## loclist = [BookID, ChapterID, VerseID]
    word_phrase_freq('hast', [1, 1, 1], [100, 100, 100], 1, 10000)
    # plotfreq('God', all_nword_freq_book('God', 0), 'whole book')
    plt.show()
