import re
import codecs
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

pos_tweets = neg_tweets = neu_tweets = 0


def set_up_api_access():
    # Tokens required for accessing twitter api
    access_token = 'xxxxx'  # insert access token
    access_token_secret = 'xxxxx'  # insert access_token_secret
    consumer_key = 'xxxxx'  # insert consumer key
    consumer_secret = 'xxxxx'  # insert consumer_secret

    # perform auth
    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        return api
    except:
        print("Err: Auth failure")


def extract_sentiment(tweet):
    # Remove unwanted special characters, url's, hashtags etc., from the tweet
    tweet = clean_tweet(tweet)

    # wrap tweet in a TextBlob obj
    textblob_tweet = TextBlob(tweet)

    # Finding sentiment. Internally Textblob uses nltk's Naive Bayes classifier by default
    if textblob_tweet.sentiment.polarity > 0:
        return 'positive'
    elif textblob_tweet.sentiment.polarity < 0:
        return 'negative'
    else:
        return 'neutral'


def clean_tweet(tweet):
    # Have taken reference from https://www.machinelearningplus.com/python/python-regex-tutorial-examples/
    tweet = re.sub('http\S+\s*', '', tweet)  # remove URLs
    tweet = re.sub('RT|cc', '', tweet)  # remove RT and cc
    tweet = re.sub('#\S+', '', tweet)  # remove hashtags
    tweet = re.sub('@\S+', '', tweet)  # remove mentions
    tweet = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), '', tweet)  # remove punctuations
    tweet = re.sub('\s+', ' ', tweet)  # remove extra whitespace
    return tweet


def get_tweets(api, hashtag, count):

    labeled_tweets = []

    try:
        tweets = api.search(q=hashtag, count=count)
        # count = 0
        for tweet in tweets:
            parsed_tweet = {'tweet': tweet.text, 'label': extract_sentiment(tweet.text)}
            # count = count + 1
            # To avoid redundant tweets in case of retweets
            if tweet.retweet_count > 0:
                if parsed_tweet not in labeled_tweets:
                    labeled_tweets.append(parsed_tweet)
                    write_tweet_to_labelfile(parsed_tweet)

            else:
                labeled_tweets.append(parsed_tweet)
                write_tweet_to_labelfile(parsed_tweet)
        # print(count)
        return labeled_tweets

    except tweepy.TweepError as ex:
        print("Err : " + str(ex))


def write_tweet_to_labelfile(parsed_tweet):
    """
    This function writes a tweet to it's respective label file
    """
    global pos_tweets, neg_tweets, neu_tweets

    if parsed_tweet['label'] == 'positive':
        with codecs.open('positive_tweets.txt', 'a+', encoding='utf-8') as out:
            out.write(parsed_tweet['tweet'])
        pos_tweets += 1

    elif parsed_tweet['label'] == 'negative':
        with codecs.open('negative_tweets.txt', 'a+', encoding='utf-8') as out:
            out.write(parsed_tweet['tweet'])
        neg_tweets += 1

    else:
        with codecs.open('neutral_tweets.txt', 'a+', encoding='utf-8') as out:
            out.write(parsed_tweet['tweet'])
        neu_tweets += 1


def main():
    # get api object
    api = set_up_api_access()

    # getting the labeled tweets
    labeled_tweets = get_tweets(api, 'ThalapathyKingOfBoxOffice', 100)
    # labeled_tweets = get_tweets(api, 'MidtermElection2018', 100)

    # pos_tweets = [tweet for tweet in labeled_tweets if tweet['label'] == 'positive']
    print("Positive tweets: {} %".format(100 * pos_tweets / len(labeled_tweets)))
    #
    # neg_tweets = [tweet for tweet in labeled_tweets if tweet['label'] == 'negative']
    print("Negative tweets: {} %".format(100 * neg_tweets / len(labeled_tweets)))
    #
    # neu_tweets = [tweet for tweet in labeled_tweets if tweet['label'] == 'neutral']
    print("Neutral tweets: {} %".format(100 * neu_tweets / len(labeled_tweets)))


if __name__ == "__main__":
    main()
