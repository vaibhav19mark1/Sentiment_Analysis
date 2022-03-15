# pip install tweepy
# pip install TextBlob
# pip install matplotlib

from ast import keyword
from cgitb import html
from genericpath import isfile
from flask import Blueprint, render_template, Request, request
import matplotlib.pyplot as plt
import os

import tweepy
import csv
import re
from textblob import TextBlob
import matplotlib 
matplotlib.use('agg')

#register this file as a blueprint
second = Blueprint("second", __name__, static_folder="static", template_folder="template")


# sentiment analyzer route
@second.route("/sentiment_analyzer")
def sentiment_analyzer():
    return render_template("sentiment_analyzer.html")


# class with main logic
class SentimentAnalysis:
    def __init__(self):
        self.tweets = []
        self.tweetText = []
    
    # this function connects to the Tweepy API
    def DownloadData(self,keyword,tweets):
        # authentication
        apiKey='5rD9iMUz5uG2V7Ir3G6aFIBjs'
        apiSecret='0BDRG08FlkXuAMNJYP6LZw5E9KSO8nOqSl8DcqEP0EX0HrvxqH'
        accessToken='1389145017676042241-StXGSOXTBTbXjb9r2Lr9eJMfc68soQ'
        accessTokenSecret='z4GpVjPwYLO1BJYbvY9cHrLMV4v3Ezxe4Qro1DoZ1uhI1'
        auth = tweepy.OAuthHandler(apiKey,apiSecret)
        auth.set_access_token(accessToken,accessTokenSecret)
        api = tweepy.API(auth,wait_on_rate_limit=True)

        # input for term to be searched and number of tweets
        # searchTerm = input("Enter keyword to search about: ")
        # NoOfTerms = int(input("Enter how many tweets to search"))
        tweets = int(tweets)

        # seraching for tweets

        self.tweets = tweepy.Cursor(
            api.search_tweets,
            q = keyword,
            lang = "en"
        ).items(tweets)

        # Open/create a file to append data to
        csvFile = open('result.csv', 'a')

        # Use csv writer
        csvWriter = csv.writer(csvFile)

        # creating some variables to store info
        polarity = 0
        positive = 0
        spositive = 0
        neutral = 0
        negative = 0
        snegative = 0

        # iterating through tweets
        for tweet in self.tweets:
            # append to temporary variable to store in csv file later.
            self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))
            
            # print (tweet.text.translate(non_bmp_map))    #print tweet's text
            analysis=TextBlob(tweet.text)
            
            # print(analysis.sentiment)  # print tweet's polarity
            # adding up polarities to find the average later
            polarity += analysis.sentiment.polarity

            # adding reactions
            if(analysis.sentiment.polarity==0):
                neutral += 1
            elif(analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.5):
                positive+=1
            elif(analysis.sentiment.polarity > 0.5 and analysis.sentiment.polarity <= 1):
                spositive+=1
            elif(analysis.sentiment.polarity < 0 and analysis.sentiment.polarity >= -0.5):
                negative+=1
            elif(analysis.sentiment.polarity < -0.5 and analysis.sentiment.polarity >= -1):
                snegative+=1

        # write to csv file
        csvWriter.writerow(self.tweetText)
        csvFile.close()

        # Find average
        neutral = self.percentage(neutral, tweets)
        positive = self.percentage(positive, tweets)
        spositive = self.percentage(spositive, tweets)
        negative = self.percentage(negative, tweets)
        snegative = self.percentage(snegative, tweets)

        # Find average reaction
        polarity/=tweets

        # printing out data
        #  print("How people are reacting on " + keyword + " by analyzing " + str(tweets) + " tweets.")
        #  print()
        #  print("General Report: ")

        htmlpolarity= "Neutral"
        # print("Neutral")
        if(analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.5):
            htmlpolarity= "Positive"   
        elif(analysis.sentiment.polarity > 0.5 and analysis.sentiment.polarity <= 1):
            htmlpolarity= "Strongly Positive"
        elif(analysis.sentiment.polarity < 0 and analysis.sentiment.polarity >= -0.5):
            htmlpolarity= "Negative"
        elif(analysis.sentiment.polarity < -0.5 and analysis.sentiment.polarity >= -1):
            htmlpolarity= "Strongly Negative"
        
        self.plotPieChart(positive, spositive, neutral, negative, snegative, keyword, tweets)
        print(polarity,htmlpolarity)
        return polarity,htmlpolarity,positive,spositive,neutral,negative,snegative,keyword,tweets

    # Remove links, special-characters from tweet
    def cleanTweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

    # Function to calculate percentage
    def percentage(self, part, whole):
        temp = 100 * float(part)/float(whole)
        return format(temp, '.2f')
    
    #Function which sets and plots the pie chart :
    def plotPieChart(self, positive, spositive, neutral, negative, snegative, keyword, tweets):
        fig=plt.figure()
        labels = ['Positive [' + str(positive) + '%]', 'Strongly Positive ['+ str(spositive) +'%]', 
        'Neutral ['+ str(neutral) +'%]','Negative ['+ str(negative) +'%]', 
        'Strongly Negative ['+ str(snegative) +'%]',]

        sizes = [positive, spositive, neutral, negative, snegative]
        colors = ['lightgreen', 'darkgreen', 'gold', 'red', 'darkred']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        strFile = r"D:\College Stuff\Projects\SentimentAnalysis\static\images\plot.png"
        if os.path.isfile(strFile):
            os.remove(strFile)
        plt.savefig(strFile)
        plt.show()

# sentiment logic route
@second.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():

    # get user of input of keyword to search and number of tweets
    keyword = request.form.get('keyword')
    tweets = request.form.get('tweets')
    sa = SentimentAnalysis()

    #set variables which can be used in the jinja supported html page
    polarity, htmlpolarity, positive, spositive, neutral, negative, snegative, keyword1, tweet1 = sa.DownloadData(keyword, tweets)
    return render_template('sentiment_analyzer.html', polarity=polarity, htmlpolarity=htmlpolarity, positive=positive, spositive=spositive,
                           negative=negative, snegative=snegative, neutral=neutral, keyword=keyword1, tweets=tweet1) 

# visualize route (route for pie chart)
@second.route('/visualize')
def visualize():
    return render_template('PieChart.html')















