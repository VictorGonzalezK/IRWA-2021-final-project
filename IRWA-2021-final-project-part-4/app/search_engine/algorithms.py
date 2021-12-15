import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer
import json
import pycountry
import re
import string
import collections
from collections import defaultdict
from array import array
import time
import numpy as np
from numpy import linalg as la
import math
import pandas as pd


def iso_leng_translate(leng):
    return pycountry.languages.get(alpha_2=leng).name.lower()

def create_stopword_dict(tweets):
    #get languages
    lang=[]
    for i in range(len(tweets)):
        lang.append((tweets[str(i)]['lang']))
    languages = set(lang)
    
    #search for the stopwords and save them in a dictionary for later usage
    lang_dict = {}
    for i in languages:     
        try:
            #transform ISO lenguage in complete name for convenience
            lang_dict [i] = set(stopwords.words(iso_leng_translate(i)))
            
        #if we don't have a stopwords available for that lenguage we just skip
        except:
            continue
        
        
    return lang_dict

def clean_data(tweet, stopwordsByLan):
        
    #get the tweet text
    og_tweet_text = (tweet['full_text']) 

    #lowercase to uniform format and split to get words
    og_tweet_text = og_tweet_text.lower()   
    og_tweet_text = og_tweet_text.split()

    #create our pattern to avoid removing #

    #remove punctuation
    tweet_text=[]
    for word in og_tweet_text:
        #maintain the links in the correct format
        if "https" not in word:
            #delete all punctuation conserving the # and @(in tweets are meaninguful)
            word = re.sub(r'[^\w\s#@]','', word)
            word = re.sub(r'_','',word)

        if word:
            tweet_text.append(word) 


    #get lenguage to filter stpowords
    tweet_lang = tweet['lang'].lower()
    #check availability of stopwors dict
    if tweet_lang in stopwordsByLan.keys():
        #if possible filter stopwords
        stop_words = set(stopwordsByLan[tweet_lang])
        clean_text = []
        for word in tweet_text:
            if word not in stop_words:
                clean_text.append(word)

    #if stopwords are not available in some lenguage just let them 
    else:
        clean_text = tweet_text    


    #stem the words with the correct format for each lenguage
    try:
        stemmer = SnowballStemmer(iso_leng_translate(tweet_lang))
        clean_text = [stemmer.stem(word) for word in clean_text]

    except:
        pass   
        
    return clean_text

def create_index(tweets, stopwordsByLan):
    """
    Impleent the inverted index
    
    Argument:
    collection of tweets
    
    Returns:
    index - the inverted index containing terms as keys and the corresponding 
    list of tweets these keys appears in (and the positions) as values.
    tf - normalized term frequency for each term in each tweet
    idf - inverse document frequency of each term
    """
    
    index = defaultdict(list) 
    
    tf = defaultdict(list)        #term frequencies of terms in tweets 
    df = defaultdict(int)         #tweet frequencies of terms in the collection
    idf = defaultdict(float)
    
    N = len(tweets)
    
    for tweet_num, tweet in tweets.items(): 
        #get the id of the tweet
        tweet_id = tweet["id"]
        #get the terms cleaned 
        terms = clean_data(tweet, stopwordsByLan)
                
        termdictTweet = {}

        for position, term in enumerate(terms): # terms in the tweet
            try:
                # if the term is already in the index for the current tweet
                # append the position to the corrisponding list
                
                termdictTweet[term][tweet_id].append(position)  
            except:
                # Add the new term as dict key and initialize the array of positions and add the position
                termdictTweet[term]=[tweet_id, array('I',[position])] #'I' indicates unsigned int (int in python)
        
        
        #normalize term frequencies
        # Compute the denominator to normalize term frequencies
        # norm is the same for all terms of a tweet.
        norm = 0
        for term, posting in termdictTweet.items(): 
            # posting is a list containing tweet_id and the list of positions for current term in current tweet: 
            # posting ==> [tweet_id, [list of positions]] 
            # you can use it to inferr the frequency of current term.
            norm+=len(posting[1])**2
        
        norm = math.sqrt(norm)


        #calculate the tf (dividing the term frequency by the above computed norm) and df weights
        for term, posting in termdictTweet.items():     
            # append the tf for current term (tf = term frequency in current tweet/norm)
            tf[term].append(np.round(len(posting[1])/norm ,4))  
            #increment the document frequency of current term (number of tweets containing the current term)
            df[term] += 1  # increment df for current term
        
        # Compute idf 
        for term in df:
            idf[term] = np.round(np.log(float(N/df[term])),4)
        
        #merge the current tweet index with the main index
        for termpage, postingpage in termdictTweet.items():
            index[termpage].append(postingpage)
                      
                    
    return index, tf, idf

def hashtagsFreq(tweets):
    hashtags = []
    for t in tweets.values():
        for hashtag in t["entities"]["hashtags"]:
            hashtags.append("#"+hashtag["text"])
    hashcount = collections.Counter(hashtags)
    hashnorm = la.norm(list(hashcount.values()))
    for h, c in hashcount.items():
        hashcount[h] = c/hashnorm
    return hashcount

def get_hashtags(tweet):
    hashtags = list()
    for hashtag in tweet["entities"]["hashtags"]:
        hashtags.append("#"+hashtag["text"])
    return hashtags

def rankTweetsOurs(terms, tweets_ids, index, idf, tf, tweets):
    """
    Perform the ranking of the results of a search based on the tf-idf weights
    
    Argument:
    terms -- list of query terms
    tweets_ids -- list of tweet ids, to rank, matching the query
    index -- inverted index data structure
    idf -- inverted document frequencies
    tf -- term frequencies
    titleIndex -- mapping between page id and page title
    
    Returns:
    resultScores --  List of ranked scores of tweets
    resultTweets --  List of ranked tweet ids
    """
    #Apply TF-IDF scoring
    tweetVectors = defaultdict(lambda: [0]*len(terms))
    queryVector = [0]*len(terms)    
    query_terms_count = collections.Counter(terms)
    query_norm = la.norm(list(query_terms_count.values()))
    for termIndex, term in enumerate(terms): 
        if term not in index:
            continue
        queryVector[termIndex]= query_terms_count[term]/query_norm * idf[term] 
        for tweetIndex, (tweet_id, postings) in enumerate(index[term]):            
            if tweet_id in tweets_ids:
                tweetVectors[tweet_id][termIndex] = tf[term][tweetIndex] * idf[term]    
    TFIDFScores = [ [np.dot(curTweetVec, queryVector), tweet_id] for tweet_id, curTweetVec in tweetVectors.items() ]
    
    
    #Once we have the scoring of TF-IDF apply variations to the ranking
    
    #Get all the tweet data from the tweet_ids 
    query_tweets = {}
    for t in tweets.values():
        if (t['id']) in tweets_ids:
            query_tweets[t['id']]=t
            
    #Look for different data to involve popularity
    #Get likes and retweets count, and also the ratio divided by its number of followers
    likes_count = []
    likesByFollow = []
    retweets_count = []
    retweetsByFollow = []

    
    for idt in tweets_ids:
        tw = query_tweets[idt]
        likes_count.append(tw["favorite_count"])
        likesByFollow.append(tw["favorite_count"]/tw["user"]["followers_count"])
        retweets_count.append(tw["retweet_count"])
        retweetsByFollow.append(tw["retweet_count"]/tw["user"]["followers_count"]) 
        
    
    #Normalize the likes and retweets among all the query output tweets
    likesnorm = la.norm(likes_count)
    retnorm = la.norm(retweets_count)
    likes_norma = [float(r/likesnorm) for r in likes_count]
    retweets_norma = [float(r/retnorm) for r in retweets_count]
    
    
    #Take care of the hsahtags freq
    hashfreq = hashtagsFreq(tweets)
    
    #Calculate the ponderation of the hashtags, we want to undervaluate tweets that add to much hashtags for spam
    #To do so we calculate 1/num of hashtags to add to the score
    #Also if it has a trend hashtag need to increase its score
    
    nhash_ponderation = []
    hashfreq_bonus = []
    for idt in tweets_ids:
        tw = query_tweets[idt]
        hashtags = get_hashtags(tw)
        
        #get the num of hashtags
        n_hash = len(hashtags)
        if n_hash==0:
            nhash_ponderation.append(0)
        else:
            nhash_ponderation.append(1/n_hash)
        
        freqs=[0]
        for h in hashtags:
            #get the frequency of hashtags
            freqs.append(hashfreq[h])
        
        #if it has a hastag of bigg frequency add it frequency to the score
        if (np.max(freqs)>=0.6):
            hashfreq_bonus.append(np.max(freqs))
        else:
            hashfreq_bonus.append(0)
        
        
    
    #Select every stat weight in the popularity score

    likes = 0.35
    rets = 0.35
    l_f = 0.05
    r_f = 0.05
    nhsh = 0.15
    fhsh = 0.05
    

    pop_scores = {}
    listids = list(tweets_ids)
    for x in range(len(listids)):
        pop_scores[listids[x]] = likes*likes_norma[x]+ rets*retweets_norma[x] + l_f*likesByFollow[x] + r_f*retweetsByFollow[x] + nhsh*nhash_ponderation[x] + fhsh*hashfreq_bonus[x]
    
                                     
    #select the value of tfid and popularity scores in the final score
    tfidfs = 0.3
    pops = 0.7
    
    tfidfnorm = la.norm([r[0] for r in TFIDFScores])
    popsnorm = la.norm(list(pop_scores.values()))
    #normalize to reduce the difference in scoring in both methods
   
    tweetScores = [ [np.dot(curTweetVec, queryVector)/tfidfnorm*tfidfs + pops*pop_scores[tweet_id]/popsnorm, tweet_id] for tweet_id, curTweetVec in tweetVectors.items() ]
    
    tweetScores.sort(reverse=True)

    
    resultTweets = [x[1] for x in tweetScores]
    resultScores = [x[0] for x in tweetScores]
    
    if len(resultTweets) == 0:
        print("No results found, try again")
        
    #return rank punctuation and ids
    return resultScores, resultTweets

def tweet_Searcher(tweets, id):
    for tweet in tweets.values():
            if (tweet['id']) == id:
                return [str(tweet['full_text']), str(tweet["user"]["name"]), str(tweet["created_at"]), ' '.join(get_hashtags(tweet)).strip(), str(tweet["favorite_count"]), str(tweet["retweet_count"]), "https://twitter.com/"+str(tweet["user"]["id"])+"/status/"+tweet['id_str'] ]
                
def query_search(query, index, stopwordsByLan, tweets, tf, idf):
    '''
    As we are working with conjunctive queries. 
    The output is either the needed data of tweets that contain all of the query terms, if scores is False, or 
    the tweet ids and the scores of tweets that contain all query terms if scores is True.
    '''
    query = clean_data(query, stopwordsByLan)
    tweet_ids = []
    for pos, term in enumerate(query):
        try: 
            #store the ids of Tweets that contain "term"                        
            termTweets = [posting[0] for posting in index[term]]
            #the first term tweet ids are aved to compute intersection with later terms
            if pos == 0:
                tweet_ids = set(termTweets)
                
            else:  
                tweet_ids = tweet_ids.intersection(termTweets)
        except:
            #term is not in index stop searching
            print("This query has no result in the collection")
            return 0
    
    
    _ , ranked_tweets = rankTweetsOurs(query, tweet_ids, index, idf, tf, tweets)
    
    return ranked_tweets

def getTweet(tweets, id):
    for tweet in tweets.values():
            if (tweet['id']) == id:
                return tweet
                
