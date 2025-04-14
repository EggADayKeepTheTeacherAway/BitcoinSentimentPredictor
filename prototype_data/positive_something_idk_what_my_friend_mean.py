from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

sid = SentimentIntensityAnalyzer()

def get_sentiment(text):
    scores = sid.polarity_scores(text)
    compound_score = scores['compound']
    if compound_score > 0.05:
        return 'positive'
    elif compound_score < -0.05:
        return 'negative'
    else:
        return 'neutral'

def get_compound(text):
    scores = sid.polarity_scores(text)
    compound_score = scores['compound']
    return compound_score

test = "shit"
print(get_sentiment("SEX?"))
print(get_sentiment(test))
print(get_compound(test))