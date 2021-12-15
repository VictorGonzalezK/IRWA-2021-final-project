import random
from textblob import TextBlob

from app.core.utils import get_random_date
from app.search_engine.algorithms import *

class SearchEngine:
    """educational search engine"""
    i = 12345

    def search(self, search_query, inverted_index, stopwords_bylang, tweets, tf, idf ):
        print("Search query:", search_query)
        #detect the lenguage of the query
        lang = "en"
        if len(search_query)>3:
            b = TextBlob(search_query)
            lang = b.detect_language()
        #every lenguage not in the database is considered as en
        if lang not in stopwords_bylang.keys():
            lang = "en"
        query = {"full_text":search_query, "lang":lang}
        ##### your code here #####
        result_ids = query_search(query, inverted_index, stopwords_bylang, tweets, tf, idf)  
        ##### your code here #####
        results = []

        for index, item in enumerate(result_ids):
            
            info = tweet_Searcher(tweets, item)
            results.append(TweetInfo(item, info, "doc_details?id={}&qname={}&qlang={}".format(item, search_query, lang), index))

        #results.sort(key=lambda doc: doc.ranking, reverse=True)

        return results


class TweetInfo:
    def __init__(self, id, info, url, ranking):
        
        self.title = info[0][:15]
        self.full_text = info[0]
        self.user= info[1]
        self.doc_date = info[2]
        self.hashtags = info[3]
        self.favs = info[4]
        self.ret = info[5]
        self.og_url = info[6]
        self.description = "Tweet: " + info[0] + "|" + "Username: " + info[1] + "|" + "Hashtags: " + info[3] + "|" + "Likes: " +  info[4] + "|" + "Retweets: "+ info[5]
        self.url = url
        self.url_text = "Get details from Tweet: " + str(id)
        self.ranking = ranking
