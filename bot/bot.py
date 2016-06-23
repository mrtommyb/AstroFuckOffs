import json
from twython import Twython
from twython import TwythonStreamer

from .db import DEFAULT_DB, FuckOffDB

from .secrets import *

# Configuration
TWITTERHANDLE = 'AstroFuckOffs'
LOGFILE = 'bot.log'
STREAMING_LOGFILE = 'streaming.log'


class InvalidTweetException(Exception):
    pass


class TweetHandler():

    def __init__(self, tweet, dbfile=DEFAULT_DB, dry_run=False):
        self.validate(tweet)
        self.tweet = tweet
        self.dbfile = dbfile
        self.db = FuckOffDB(self.dbfile)
        self.dry_run = dry_run

    def validate(self, tweet):
        if 'text' not in tweet:
            raise InvalidTweetException('{} does not look like a status.'.format(tweet['id']))
        if 'retweeted_status' in tweet:
            raise InvalidTweetException('{} is a retweet.'.format(tweet['id']))
        if tweet['user']['screen_name'] == TWITTERHANDLE:
            raise InvalidTweetException('{} posted by {}.'.format(tweet['id'], TWITTERHANDLE))

    def get_recipients(self):
        """Returns the recipients of the star as a list of dictionaries."""
        recipients = []
        for mention in self.tweet['entities']['user_mentions']:
            screen_name = mention['screen_name']
            if ((screen_name != TWITTERHANDLE) and
                    (screen_name not in recipients) and
                    (self.tweet['text'][mention['indices'][1]] == '+')):
                recipients.append(mention)
        return recipients  # unique recipients only

    def handle(self):
        """Save stars to the database and tweet the responses."""
        responses = []
        recipients = self.get_recipients()
        print(self.tweet['user']['screen_name'])
        if self.tweet['user']['screen_name'] in [rec['screen_name'] for rec in recipients]:
            text = ("@{} I'm sorry, {}. "
                    "I'm afraid I can't do that.".format(
                        self.tweet['user']['screen_name'],
                        self.tweet['user']['name'].split(' ')[0]))
            self.post_tweet(status=text, in_reply_to_status_id=self.tweet['id'])
            return [text]
        for recipient in recipients:
            # Save the transaction in the db
            self.db.add(donor=self.tweet['user'],
                        recipient=recipient,
                        tweet=self.tweet)
            # Create the tweet
            url = 'https://twitter.com/{}/status/{}'.format(self.tweet['user']['screen_name'], self.tweet['id'])
            text = ('@{} Bad news, '
                    'you just got told to fuck off by @{}! Your total is {}. '
                    '{}'.format(
                            recipient['screen_name'],
                            self.tweet['user']['screen_name'],
                            self.db.count_stars(recipient['id']),
                            url))
            responses.append(text)
            self.post_tweet(status=text, in_reply_to_status_id=self.tweet['id'])
        return responses

    def post_tweet(self, status, in_reply_to_status_id):
        if not self.dry_run:
            twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
            result = twitter.update_status(status=status,
                                           in_reply_to_status_id=in_reply_to_status_id)
            with open(LOGFILE, 'a') as log:
                log.write(json.dumps(result))
            return twitter, result


class FuckOffStreamer(TwythonStreamer):

    def __init__(self):
        super(FuckOffStreamer, self).__init__(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    def on_success(self, data):
        try:
            with open(STREAMING_LOGFILE, 'a') as log:
                log.write(json.dumps(data))
                TweetHandler(data).handle()
        except Exception as e:
            print('ERROR! {}'.format(e))

    def on_error(self, status_code, data):
        print('STREAMER ERROR: {}'.format(status_code))


def run():
    stream = FuckOffStreamer()
    stream.statuses.filter(track='@'+TWITTERHANDLE)


if __name__ == '__main__':
    run()
