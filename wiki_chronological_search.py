import pandas as pd
import nltk
import re
import wikipedia
from sklearn.decomposition import NMF, LatentDirichletAllocation
import numpy as np
import matplotlib.pyplot as plt
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import time
import parsedatetime
import sys
import math

lemm =nltk.stem.WordNetLemmatizer()

class LemmaTfidfVectorizer(TfidfVectorizer):
    def build_analyzer(self):
        analyzer = super(LemmaTfidfVectorizer, self).build_analyzer()
        return lambda doc: (lemm.lemmatize(w) for w in analyzer(doc))

def processing(all_events, number_of_search_results):
    
    p = parsedatetime.Calendar()
    datetime_tuples = []
    for i in all_events:
        datetime_tuples.append(p.parse(i))
    
    year = []
    month = []
    day = []
    valid_or_invalid = []
    events = []
    
    for datetime_tuple in datetime_tuples:
        year.append(datetime_tuple[0][0])
        month.append(datetime_tuple[0][1])
        day.append(datetime_tuple[0][2])
        valid_or_invalid.append(datetime_tuple[1])
    
    top_events = pd.DataFrame({'Top_Events': all_events,
                               'Year': year,
                               'Month': month,
                               'day': day,
                               'valid_or_invalid': valid_or_invalid})
    
    valid_top_events = top_events[top_events.valid_or_invalid != 0]
    events = valid_top_events['Top_Events'].tolist()
    
    if events != []:
        tfidf_vectorizer =LemmaTfidfVectorizer(max_df=0.95, min_df=2, stop_words='english',decode_error='ignore' )
        tfidf_vectorizer.fit(events)
        tfidf_event_score = []

        for i in events:
            vector = tfidf_vectorizer.transform([i])
            tfidf_event_score.append(sum(vector.toarray()[0]))

        valid_top_events['Score'] = tfidf_event_score
        valid_top_events = valid_top_events.sort_values(by=['Year','Score'], ascending = [True, False]).reset_index(drop=True)
        no_of_unique_years = len(valid_top_events.Year.unique())
        years = valid_top_events.Year.unique()

        display_events = pd.DataFrame(columns=valid_top_events.columns)

        counter_1 = 0 
        counter_2 = 0
        for i in range(int(number_of_search_results)):
            if counter_1 < no_of_unique_years:
                yr = years[counter_1]
                counter_1 += 1
            else:
                counter_1 = 0
                counter_2 += 1
                yr = years[counter_1]
            try:
                display_events = display_events.append(valid_top_events[valid_top_events['Year']==yr].iloc[counter_2,:],ignore_index=True)
            except:
                pass

        display_events = display_events.sort_values(by=['Year','Score'], ascending = [True, False]).reset_index(drop=True)

    
    else:
        return

    return display_events.Year, display_events.Top_Events
    

def wiki_search(search_phrase, number_of_search_results):

    phrase_tokens = nltk.word_tokenize(search_phrase.lower())
    phrase_len = len(phrase_tokens)
    all_related_phrases = []
    flag = False
    
    try:
      page = wikipedia.page(search_phrase)
    except wikipedia.exceptions.DisambiguationError as e:
      all_related_phrases = e.options
    except wikipedia.exceptions.PageError as e:
      return 

    if all_related_phrases==[]:
        all_related_phrases = wikipedia.search(search_phrase)
    
    all_related_phrases_relevant = []
    
    for phrase in all_related_phrases:
        alternative_phrase_tokens = nltk.word_tokenize(phrase.lower())
        flag = set(phrase_tokens).issubset(set(alternative_phrase_tokens))
        if flag:
            all_related_phrases_relevant.append(phrase)

    all_events = []

    if all_related_phrases_relevant != []:
        try:
            for i in all_related_phrases_relevant:
                data = wikipedia.page(i).content
                required_data, _ , _ = data.partition('== See also ==')
                required_data = nltk.sent_tokenize(required_data)
                events = [line.rstrip() for line in required_data] 
                cleaned_events = []
                for line in events:
                    if line:
                        line = line.replace('\n', ' ')
                        cleaned_events.append(re.sub(r'=[0-9a-zA-Z_\D]*=', r'', line))
                all_events.extend(cleaned_events)
                
        except:
            pass
    else:
        return

    data = processing(all_events, number_of_search_results)
    
    if data is not None:
        years, events = data[0], data[1]
    else:
        return
        
    return years, events