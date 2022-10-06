import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def main():
    news = get_news()
    scores = get_sentiment(news)
    plot(scores)


def get_news():
    # Input
    symbol = input('Enter a ticker: ')
    print('Getting data for ' + symbol + '...\n')

    # Set up scraper
    url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    html = soup(webpage, "html.parser")

    try:
        # Find news table
        news = pd.read_html(str(html), attrs={'class': 'fullview-news-outer'})[0]
        links = []
        for a in html.find_all('a', class_="tab-link-news"):
            links.append(a['href'])

        # Clean up news dataframe
        news.columns = ['date', 'headline']
        news['link'] = links
        news['date'] = pd.to_datetime(news['date'], dayfirst=True)
        news['date'] = [d.date() for d in news['date']]
        return news

    except Exception as e:
        return e


def get_sentiment(news):
    vader = SentimentIntensityAnalyzer()
    news['compound'] = news['headline'].apply(lambda score: vader.polarity_scores(score)['compound'])
    news['sentiment'] = news['compound'].apply(lambda c: 'pos' if c > 0 else('neg' if c < 0 else 'neutral'))
    return news


def plot(scores):
    scores['sentiment'].value_counts().plot(kind='bar')
    plt.show()


if __name__ == '__main__':
    main()