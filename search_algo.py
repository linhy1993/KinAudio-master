import time
import requests
from flask import request
import nltk

nltk.download('wordnet')
import json
import math
from nltk.corpus import wordnet as wn
from textblob import TextBlob
import operator

number_of_items_to_retrieve_from_db = 100
top_n_words = 5


###########################
## Get Keywords From API ##
###########################
# def get_keywords_from_api():
#     r = requests.get(keys_api_url)
#     return json.loads(r.text)


##########################
## Get Keywords From DB ##
##########################
# *
def get_keywords_from_db():
    r = requests.get("https://leo-web-app.azurewebsites.net/send-data")
    return json.loads(r.text)

def get_news_by_id(db_result, id):
    result = ''
    for news in db_result:
        if news['id'] == id:
            result = news
            break

    #print(result)
    return result


######################
## Compare Keywords ##
######################
def compare_keywords(words='[{"word": "cat", "pos": "NOUN"}, {"word": "dog", "pos": "NOUN"}]'):
    # pos can be VERB, NOUN, ADJ and ADV
    words = json.loads(words)

    if len(words) != 2:
        return ("Please send two word to compare. right now you sent {} word(s).".format(len(words)))
        exit()
    elif 'word' not in words[0] or 'word' not in words[1]:
        return (
            'Please send your request as a string like this line (include "[]"): [{"word": "cat", "pos": "NOUN"}, {"word": "dog", "pos": "NOUN"}] and note that "pos" attribute is not required and by default it will determined as "NOUN" but you can set it as VERB, NOUN, ADJ and ADV.')
        exit()
    else:
        # Set Default values
        if 'pos' not in words[0]:
            words[0]["pos"] = "noun"

        if 'pos' not in words[1]:
            words[1]["pos"] = "noun"

        # make positions to lowercase to avoid conflict!
        words[0]["pos"] = words[0]["pos"].lower()
        words[1]["pos"] = words[1]["pos"].lower()

    def return_wn_position(pos_str):
        if pos_str == "noun":
            return wn.NOUN
        elif pos_str == "verb":
            return wn.VERB
        elif pos_str == "adj":
            return wn.ADJ
        elif pos_str == "adv":
            return wn.ADV
        else:
            # Default State!
            return wn.NOUN

    synsets1 = wn.synsets(words[0]["word"], pos=return_wn_position(words[0]["pos"]))
    synsets2 = wn.synsets(words[1]["word"], pos=return_wn_position(words[1]["pos"]))

    if len(synsets1) == 0 or len(synsets2) == 0:
        # print("There isn't enough synsets to do compare. number or synsets for '{}' is {} and for '{}' is {}.".format(words[0]["word"], len(synsets1), words[1]["word"], len(synsets2)))
        return 0

        # print (synsets1[0])
    max = 0
    for syn in synsets1[:1]:
        # print (syn, "Definition is:", syn.definition(), "\n")
        for syn2 in synsets2[:1]:
            # print (syn, "similarity with ", syn2, "is:", syn.path_similarity(syn2))
            temp = syn.path_similarity(syn2)
            if (temp > max):
                max = temp

    return max

    # print (words)




# compare_keywords('[{"word": "Dog"}, {"word": "Cat"}]')


def search_algo(key_words):
    # result = compare_keywords('[{"word": "Dog"}, {"word": "Cat"}]')
    api_keywords = key_words
    db_result_raw = get_keywords_from_db()
    # for api_keyword in api_keyword
    db_result = []
    for str_row in db_result_raw:
        row = json.loads(str_row)
        dict = {"id": row["_id"]["$oid"], "sum": row["summary"], "link": row["href"],"title": row["title"]}
        print(dict)
        db_result.append(dict)

    temp = ""
    start = time.clock()
    final_list = []
    for api_keyword in api_keywords:
        for row in db_result:
            summary = row["sum"]
            # loop inside the keywords
            for item in summary:
                # db_keywords.append(item.encode('utf-8'))#Human Usage for UTF Output on windows console!
                temp_text = TextBlob(item)

                for word in temp_text.words:
                    # print (word.encode('utf-8'))
                    compare_str = '[{"word": "' + api_keyword + '", "pos": "NOUN"}, {"word": "' + str(
                        word) + '", "pos": "NOUN"}]'
                    max_score = compare_keywords(compare_str)
                    final_list.append([max_score, row["id"]])


    sorted_list = sorted(final_list, key=lambda item: item[0], reverse=True)

    counter = 0
    hit_news = [];
    for score in sorted_list:
        #IDs.append(str(score[1]))
        id = str(score[1])
        #one['summary'] =
        hit = get_news_by_id(db_result,id)
        hit_news.append(hit)

        counter += 1
        if counter >= top_n_words:
            break


    return hit_news  # return "Send Your Request."
