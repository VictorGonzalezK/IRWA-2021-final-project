from datetime import datetime
import json


class AnalyticsData:
    fact_clicks = dict([])
    fact_query = []
    fact_users = dict([])
    fact_request = []


    def set_clicks(self,clicks):
        self.fact_clicks=clicks

    def set_queries(self,queries):
        self.fact_query=(queries)

    def set_users(self,users):
        self.fact_users=users

    def set_requests(self,requests):
        self.fact_request=requests

class Click:
    def __init__(self, tweet_id, qname, qlang, enterTime):
        self.tweet_id = tweet_id
        self.qname = qname
        self.qlang = qlang
        self.enterTime = enterTime

    def getDwellTime(self):
        exitTime= datetime.now()
        self.dwelTime = exitTime-self.enterTime


class Query:
    def __init__(self, n_terms, terms, results):
        self.n_terms = n_terms
        self.terms = enumerate(terms)
        self.q_results = results
        
class User:
    def __init__(self, browser, OS, datetime, IP, city, country):
        self.browser = browser
        self.OS = OS
        self.datetime = datetime
        self.date = datetime.date()
        self.time = datetime.time()
        self.hour = datetime.hour
        self.minute = datetime.minute
        self.IP = IP
        self.country = country
        self.city = city
        

class Requests:
    def __init__(self, datetime, request):
        self.datetime = datetime
        self.request = request
    
