from __future__ import unicode_literals
from hazm import *
import json
import string
from parsivar import FindStems
from hazm import Stemmer
from collections import Counter


def read_file():
    document = []
    f = open('jsonfile_data.json', "r")
    data = json.loads(f.read())
    for item in data:
        document.append(data[item]['content'])
    f.close()
    return document


def delete_punctuation(document):
    punctuations = string.punctuation
    punctuations += "".join(['،', '؟', '؛', '»', '«'])
    return document.translate(str.maketrans('', '', punctuations))


def normalize(document):
    normalizer = Normalizer()
    return normalizer.normalize(document)


def tokenize(document):
    return word_tokenize(document)


def stem(document):
    stemmer = Stemmer()
    return stemmer.stem(document)


'''
first we check if the word is a stop word
if it is not then we save the docID and its index in it
'''


def positional_index():
    positional_index_list = {}
    f = open('jsonfile_data.json', "r")
    data = json.loads(f.read())
    for item in data:
        myContent = data[item]['content']
        myContent = delete_punctuation(myContent)
        myContent = normalize(myContent)
        myContent = tokenize(myContent)
        stopWord = set(stopwords_list())
        for position, word in enumerate(myContent):
            if word not in stopWord:
                word = stem(word)
                if word in positional_index_list:  # we have the word in positional index
                    positional_index_list[word][0] += 1  # for frequency
                    if item in positional_index_list[word][1]:  # we have the doc id
                        positional_index_list[word][1][item].append(position)
                    else:  # we dont have the doc id
                        positional_index_list[word][1][item] = [position]
                else:
                    list_doc = []
                    list_doc.append(1)
                    doc_ID = {}
                    doc_ID[item] = [position]  # position is the index of the word
                    list_doc.append(doc_ID)  # dictionary for ids
                    positional_index_list[word] = list_doc  # dictionary for positional index

    return positional_index_list


'''
search the query in the positional index list and return the doc id
if it is just some words it check each of the and return a list of doc id's with the priority of frequency
'''


def search_query(positional_index_list):
    positions = {}
    print("enter your Query :) :")
    query = input()
    query = word_tokenize(query) # now query is a list of words searched by user

    id_s = []  # we save the doc id having the word and a frequency for the doc id of how many of the words it had
    id_s_not = []  # save the doc id's for "not" words
    quotation_first = False
    quotation_second = False
    for j in range(len(query)):
        word = query[j]
        if word == '"':
            if quotation_first:
                quotation_second = True
                quotation_first = False
            else:
                quotation_first = True

            if quotation_second:
                for id in positions:
                    id_s.append(int(id))
            continue
        word = normalize(word)
        word = stem(word)

        if word in positional_index_list:
            doc_ID = positional_index_list[word][1]
            positions1 = positions
            positions = {}
            for id in doc_ID:
                # id = doc_ID[i][0]
                if j != 0 and query[j - 1] != '!':
                    if quotation_first:
                        if query[j - 1] == '"':
                            positions[id] = doc_ID[id]
                        else:
                            for index in positions1:
                                if index == id :
                                    for position1 in positions1[index]:
                                        for position2 in doc_ID[id]:
                                            if position2 - 1 == position1:
                                                if id not in positions:  # new position
                                                    positions[id] = [position2]
                                                else:  # we had the position
                                                    positions[id].append(position2)

                    else:
                        id_s.append(int(id))
                elif j != 0 and query[j - 1] == '!':
                    id_s_not.append(int(id))
                else:
                    id_s.append(int(id))
    id_s = sort_doc_id_s(id_s)
    id_s_not = sort_doc_id_s(id_s_not)
    list_result = subtract_list(id_s, id_s_not)
    return list_result


'''
in this function we sort the list by its frequency and then remove the duplicates
'''


def sort_doc_id_s(doc_list):
    doc_list = [key for key, value in Counter(doc_list).most_common()]
    return doc_list


'''
subtracts one list from the other list
'''


def subtract_list(list_first, list_second):
    res = []
    for item in list_first:
        if item not in list_second:
            res.append(item)
    return res


'''
we have the doc ids, we get the URL and title
'''


def return_URL_title(doc_ids):
    f = open('jsonfile_data.json', "r")
    data = json.loads(f.read())
    j = []
    urls = []
    titles = []
    for i in doc_ids:
        j.append(i)
        urls.append(data[str(i)]['url'])
        titles.append(data[str(i)]['title'])

    f.close()
    return urls, titles, j


if __name__ == '__main__':
    positional_index_list = positional_index()
    doc_ids = search_query(positional_index_list)
    urls, titles, j = return_URL_title(doc_ids)
    if len(urls) == 0:
        print("No Result For Your Search! :(")
    for i in range(len(urls)):
        print(i, ')\n', 'doc id:', j[i], '\nURL:\n', urls[i], "\ntitle:\n ", titles[i])
        if i == 5:
            exit(0)  # easy easy tamam tamam
