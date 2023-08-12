import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import nltk
import ssl
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import date, timedelta


try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	pass
else:
	ssl._create_default_https_context = _create_unverified_https_context

nltk.downloader.download('vader_lexicon')


def main():
	parsed = get_news()
	scores = get_sentiment(parsed)
	plot(scores)


def get_news():
	# Input
	ticker = input('Enter a ticker: ')
	print('Getting data for ' + ticker + '...\n')

	# Set up scraper
	url = ("https://finviz.com/quote.ashx?t=" + ticker.lower())
	#req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	req = Request(url=url, headers={'user-agent': 'news'})
	webpage = urlopen(req).read()
	html = soup(webpage, "html.parser")

	# Find news table
	news_table = html.find(id = 'news-table') # gets the html object of entire table
	ignore_source = ['Motley Fool', 'TheStreet.com'] # sources to exclude
	print(news_table)

	date_allowed = []
	start = input("Enter the date/press enter for today's news (Ex: Dec-27-20) or 'All' for all the available news: ")
	if len(start) == 0:
		start = date.today().strftime("%b-%d-%y")   
		date_allowed.append(start)
	
	parsed = []    
	for row in news_table.findAll('tr'):  # for each row that contains 'tr'
		title = row.a.text
		source = row.span.text
		date = row.td.text.split(' ')
		print(date)
		if len(date) > 1:     # both date and time, ex: Dec-27-20 10:00PM
			date1 = date[0]
			time = date[1]
		else:time = date[0] # only time is given ex: 05:00AM

		if source.strip() not in ignore_source:
			if start.lower() == 'all':
				parsed.append([ticker, date1, time, title])                                
			elif date1 in date_allowed:
				parsed.append([ticker, date1, time, title])                
			else: break
	
	return parsed

def get_sentiment(parsed):
	df = pd.DataFrame(parsed, columns=['Ticker', 'date', 'Time', 'Title'])
	vader = SentimentIntensityAnalyzer()
	# for every title in data set, give the compund score
	score = lambda title: vader.polarity_scores(title)['compound']
	df['compound'] = df['Title'].apply(score)   # adds compund score to data frame
	print(df)

	return df


def plot(df):
	# Visualization of Sentiment Analysis
	df['compound'].value_counts().plot(kind='bar')

	plt.show()


if __name__ == '__main__':
	main()