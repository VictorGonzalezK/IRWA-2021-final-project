from flask.wrappers import Request
import nltk
from flask import Flask, render_template
from flask import request, session

from datetime import datetime
from ip2geotools.databases.noncommercial import DbIpCity
import collections


import pickle
import os.path

from app.analytics.analytics_data import AnalyticsData, Click, Query, User, Requests
from app.core import utils
from app.search_engine.search_engine import SearchEngine, TweetInfo

from app.search_engine.algorithms import create_stopword_dict, create_index, get_hashtags, tweet_Searcher

app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
#app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
#app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

searchEngine = SearchEngine()
analytics_data = AnalyticsData()

#Load all analytics data if any is available locally

if os.path.isfile('analytics_data_queries.pkl'):
    with open('analytics_data_queries.pkl','rb') as f:
        queries = pickle.load(f)
        analytics_data.set_queries(queries)
    f.close()

if os.path.isfile('analytics_data_clicks.pkl'):
    with open('analytics_data_clicks.pkl','rb') as f:
        clicks = pickle.load(f)
        analytics_data.set_clicks(clicks)
    f.close()

if os.path.isfile('analytics_data_users.pkl'):
    with open('analytics_data_users.pkl','rb') as f:
        users = pickle.load(f)
        analytics_data.set_users(users)
    f.close()
#import tweets and create stopword dict and inverted index
tweets = utils.load_documents_corpus()
stopwords_bylang = create_stopword_dict(tweets)
print("Calculating inverted index....")
inverted_index, tf, idf = create_index(tweets, stopwords_bylang)

@app.route('/')
def search_form():

    #session['some_var'] = "IRWA 2021 home"

    u = request.user_agent
    time = datetime.now()

    geo = DbIpCity.get(request.remote_addr, api_key='free')
    user = User(u.browser, u.platform, time, request.remote_addr, geo.city, geo.country)
    
    if (request.remote_addr) in analytics_data.fact_users.keys():
        if u.browser not in [x.browser for x in analytics_data.fact_users[request.remote_addr]]:
            analytics_data.fact_users[request.remote_addr].append(user)
    else:
        analytics_data.fact_users[request.remote_addr] = [user]

    with open('analytics_data_users.pkl', 'wb') as f:
        pickle.dump(analytics_data.fact_users, f)
    

    f.close()
    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']

    results = searchEngine.search(search_query, inverted_index, stopwords_bylang, tweets, tf, idf)
    found_count = len(results)

    #session['last_found_count'] = found_count
    analytics_data.fact_query.append(Query(len(search_query.split()), search_query.split(), found_count))
    
    with open('analytics_data_queries.pkl', 'wb') as f:
        pickle.dump(analytics_data.fact_query, f)

    f.close()
    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():


    # getting request parameters:
    # user = request.args.get('user')
    clicked_tweet_id = int(request.args["id"])
    clicked_tweet_qname = request.args["qname"]
    clicked_tweet_qlang = request.args["qlang"]
    
    click_time = datetime.now()
    click = Click(clicked_tweet_id, clicked_tweet_qname, clicked_tweet_qlang, click_time)


    #print("click in id={} - fact_clicks len: {}".format(clicked_tweet_id, len(analytics_data.fact_clicks)))
    t = tweet_Searcher(tweets,clicked_tweet_id)
    

    if clicked_tweet_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_tweet_id].append(click)
    else:
        analytics_data.fact_clicks[clicked_tweet_id] = [click]
    
    with open('analytics_data_clicks.pkl', 'wb') as f:
        pickle.dump(analytics_data.fact_clicks, f)

    f.close()
    return render_template('doc_details.html', tweet = TweetInfo(clicked_tweet_id, t, "doc_details?id={}".format(clicked_tweet_id), 0), stats = "/stats?id={}".format(clicked_tweet_id))


@app.before_request
def do_something_whenever_a_request_comes_in():
    # request is available
    analytics_data.fact_request.append(Requests(datetime.now(),request))


    f.close()
@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """
    ### Start replace with your code ###
    arr_t_clicks =[]
    t_id = int(request.args["id"])
    if t_id in analytics_data.fact_clicks.keys():
        arr_t_clicks = analytics_data.fact_clicks[t_id]
        num_clicks = len(arr_t_clicks)
    return render_template('stats.html', clicks_data=arr_t_clicks, n_clicks=num_clicks)
    ### End replace with your code ###


@app.route('/dashboard', methods=['GET'])
def dashboard():
    
    clicked_t_ids = []
    clicked_t_counts = []
    clicked_t_hashtags = []
    
    for t_id in analytics_data.fact_clicks.keys():
        clicked_t_ids.append(t_id)
        clicked_t_counts.append(len(analytics_data.fact_clicks[t_id]))
        t = tweet_Searcher(tweets,t_id)[3].split()*len(analytics_data.fact_clicks[t_id])
        for i in t:
             clicked_t_hashtags.append(i)

    hsizes_count = collections.Counter(clicked_t_hashtags)
    n_h =[]
    counth=[]
    for n, count in hsizes_count.items():
        n_h.append(n)
        counth.append(count)


    query_sizes = []
    for q in analytics_data.fact_query:
        query_sizes.append(q.n_terms)
    qsizes_count = collections.Counter(query_sizes)
    n_q =[]
    countq=[]
    for n, count in qsizes_count.items():
        n_q.append(n)
        countq.append(count)

    
    pref_browser_list = []
    for user in analytics_data.fact_users.keys():
        for u in analytics_data.fact_users[user]:
            pref_browser_list.append(u.browser)   
    pref_browser = collections.Counter(pref_browser_list)
    b_q =[]
    countb=[]
    for n, count in pref_browser.items():
        b_q.append(n)
        countb.append(count)

    return render_template('dashboard.html', clicked_t_ids=clicked_t_ids, clicked_t_counts=clicked_t_counts, countq=countq, n_q=n_q , countb=countb, b_q=b_q, counth=counth,n_h=n_h)




@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":
    app.run(port="8088", host="0.0.0.0", threaded=False, debug=False)
