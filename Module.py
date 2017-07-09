from tweepy.auth import OAuthHandler
from textblob import TextBlob
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import csv
import pandas as pd
import tweepy
import re
import time

def twitter(search):
    """
    Search accepts only data in '#Analytics OR INDIA'
    """
    ckey = ""  #Consumer Key
    csecret = ""  #Consumer Secret
    atoken = ""   #Access Token
    asecret = ""       #Access Secret

    auth = tweepy.AppAuthHandler(ckey,csecret)      #Uses Aplication Only Authentication
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True) 
    api = tweepy.API(auth)
    
    tweet=[]  #Storing Tweet
    
    #searchQuery = '#RishabPant OR #Analytics OR #INDIA'
    searchQuery = search
    
    for temp in tweepy.Cursor(api.search,q=searchQuery).items(200): #Extracting the tweet & storing into 'tweet'
        tweet.append(temp.text) 
    
    #After Pre-Processing store the new Result into 'process_tweet'    
    process_tweet = pre_process(tweet)
    
    #Storing new list into tweet_list    
    tweet_list = removing_stopwords(process_tweet)
    
    #Getting Action of Tweet
    Action,Subjectivity = senti_tweets(tweet_list)
    
    #Feature Extraction of tweet & Clustering 
    feature_extraction(tweet_list)
    
    #Writing Tweet into csv
    print print_csv(tweet_list,Action,Subjectivity)
    
#After extracting tweet 
#Staring removing comma,special charater, from tweet    
def pre_process(temp):
    pp_tweets = []     #Pre-processing Tweets
    for line in temp:
        if not'RT @' in line:
            #a = line.encode('ascii','ignore')
            a = re.sub('(\\n|\\r|,|\#|&amp;*|\\s{2,})',' ',line)+r""        
            a = re.sub('(https:|http:|http)\/*\/*((\\w.)*\/*(\\w+|0-9))?',' ',a)        
            a = re.sub('(RT)?\s*@{1}[\w]*:?','',a) 
            a = re.sub('!*','',a)
            a = re.sub('\.*','',a)  
            a = re.sub('(:|via|\[|\]|-|\(|\)|\?|\$|_|\||\/|&gt;|[0-9])','',a)
            a = re.sub('\"','\'',a)            
            a = re.sub('\\s{2,}',' ',a)
            a = ' '.join(a.split()) 
            a = a.encode('ascii','ignore') 
            #a = line.encode('ascii','ignore')
            pp_tweets.append(a)
    print "Successfully Preprocessed"
    return pp_tweets    
    
#Removing Stopewords
def removing_stopwords(status):
    stop = set(stopwords.words("english"))
    temp_list = []
    new_list = []         #Removing Stopwords & stroing in Tweet_list
    for i in range(len(status)):
        temp_list=[]
        for j in status[i].lower().split():
            if j not in stop:
                temp_list.append(j)
        new_list.append(' '.join(temp_list))  
    print "Successfully Removed Stopwords"    
    return new_list
    
#Finding whether the tweet is postive or not 
def senti_tweets(status):
    pos_neg = []
    subject = []
    pos = 0
    neg = 0    
    for i in range(len(status)):
        bb = TextBlob(status[i])
        subject.append(bb.sentiment[1])
        if(bb.sentiment[0]>0.0):
            pos_neg.append("Positive")
            pos = pos + 1
        elif(bb.sentiment[0]==0.0):
            pos_neg.append("Neutral")
        else:
            pos_neg.append("Negative")
            neg = neg + 1
    print "Positivity in Tweet : ",(pos/float(len(status)))*100,"%"
    print "Negativity in Tweet : ",round((neg/float(len(status)))*100,3),"%"
    return pos_neg,subject

#Extracting the feature
def feature_extraction(tweet):
    tfidf_vectorizer = TfidfVectorizer(use_idf=True, ngram_range=(1,5))  
    tfidf_matrix = tfidf_vectorizer.fit_transform(tweet)  
    feature_names = tfidf_vectorizer.get_feature_names() # num phrases  
    
    num_clusters = 5 
    km = KMeans(n_clusters=num_clusters)  
    km.fit(tfidf_matrix)    

    print('\n')
    print('\n')
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    for i in range(num_clusters):
        print "Cluster ",i," : ",
        for j in order_centroids[i,:5]:
            print feature_names[j],",",
        print "\n"


#Storing the result into CSV
def print_csv(text,pos_neg,subject):
    file_name = 'data'+'_'+time.strftime('%Y%m%d_%H%M%S')+'.csv'
    with open(file_name,"wb") as output:        
        writer = csv.writer(output,lineterminator='\n')
        writer.writerow(["Tweet Text","Action","Subjectivity"])
        for i in range(len(text)):
            writer.writerow([text[i],pos_neg[i],subject[i]])
    return"Successfully Writing"  

twitter('#Fashion OR #PlasticBeads')