"""
<!-- md -->
# Data Scrapping
- Below code is to scrap the data from SkingAlpha website where publicly listed companies data is available.
- selenium webdriver and BeautifulSoup libraries are used to scrap the data from website
<!-- end-md -->
"""

# Standard Libraries
import pandas as pd
from datetime import datetime,time
import numpy as np
import matplotlib.pyplot as plt

# Scraping Libraries
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import re

# NLP Libraries
from textblob import TextBlob
import textstat

# Functions
def getSentimentScore(text):
    return TextBlob(str(text)).sentiment.polarity
    
def getSubjectivity(text):
    return TextBlob(str(text)).sentiment.subjectivity

def getSentiments(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

def open_browser(alt_user_name = 'Thank you for your website'):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument(f'user-agent={alt_user_name}')
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver

# Scraping urls of each transcript before the next step.
browser         = open_browser()
list_of_dicts   = []
comp_list = ['AAPL','TSLA']
#b_url='https://seekingalpha.com/earnings/earnings-call-transcripts/'
base_url1 = 'https://seekingalpha.com/search?q='
base_url2 = '&type=keyword&tab=transcripts'
#get URLs to be scrapped - Approx 10 URLs/page
for sym in comp_list:
    browser = open_browser("Y'all are great1")
        # I put in a "unique" user agent name to help throw
        # off the captcha.  This worked for only so long.
    url_list = []
    current_ts_list = base_url1+sym+base_url2
    browser.get(current_ts_list)
    #print("URL Open",current_ts_list)
    elements_list = browser.find_elements_by_class_name('item-link')
    #print("here",elements_list[:1])
    urls    = [el.get_attribute('href') for el in elements_list]
    #headers = [el.text for el in elements_list]
    print('no of urls:', len(urls))
browser.close()
for ts_num in range(1,len(urls)):
    print('Opening url:',urls[ts_num])
    browser.get(urls[ts_num])
    soup                    = BeautifulSoup(browser.page_source)
    p_elements              = [item.text for item in soup.find_all('p')]
    title                   = p_elements[0]
    print('scraping ',ts_num,' - ',title)
    sleep(20)

    # Finding the seperation between main speech(es) and QA section
    done = False
    for item_num in range(len(p_elements)):
        if done == True:
            break
        elif p_elements[item_num] == 'Question-and-Answer Session':
            pre_QA_title         = p_elements[:item_num - 1]
            post_QA_title         = p_elements[item_num:]
            done                  = True
        else:
            pass
        
    #speech = ' '.join([i for i in pre_QA_title if len(i) >= 35][1:])
    speech = ' '.join([i for i in pre_QA_title])
    #QA     = ' '.join([i for i in post_QA_title if len(i) >= 25])
    QA     = ' '.join([i for i in post_QA_title])
    speech_score = getSentimentScore(speech)
    QA_score = getSentimentScore(QA)
    current_dict = {
        'qtr_year'                  : re.findall("Q\d[1-4]\s\d{4}",title)[0],
        'title'                     : title,
        'ticker'                    : title[title.find(":")+len(":"):title.rfind(")")],
        'speech'                    : speech,
        'speech_sentiment_score'    : speech_score,
        'speech_subjectivity'       : getSubjectivity(speech),
        'speech_complexity'         : textstat.gunning_fog(speech),
        'speech_overall_sentiments' : getSentiments(speech_score), 
        'Q_and_A'                   : QA,
        'QA_sentiment_score'        : QA_score,
        'QA_subjectivity'           : getSubjectivity(QA),
        'QA_complexity'             : textstat.gunning_fog(QA),
        'QA_overall_sentiments'     : getSentiments(QA_score)
    }
    list_of_dicts.append(current_dict)

#convert data to dataframe
df = pd.DataFrame(list_of_dicts, columns = ['qtr_year','title','ticker', 'speech', 
                                            'speech_sentiment_score','speech_subjectivity', 'speech_complexity', 'speech_overall_sentiments'
                                            'Q_and_A','QA_sentiment_score','QA_subjectivity','QA_complexity','QA_overall_sentiments'])

#write to excel - export data
#path = f_n = 'G:\\Project\\Git_Repos\\NLP-Earning-call-analysis\\Data\\NLP_conf_call_data.xlsx'
df.to_excel("../Data/NLP_conf_call_data.xlsx")