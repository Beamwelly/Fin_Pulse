from textblob import TextBlob

def analyze_sentiment(text):
    """
    Analyze the sentiment of a news article.
    Returns polarity (-1 to 1) and sentiment category.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = 'Positive'
    elif polarity < -0.1:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    return polarity, sentiment
