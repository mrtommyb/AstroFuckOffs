import json
from twython import Twython
from twython import TwythonStreamer

from .db import DEFAULT_DB, GoldStarDB

from .secrets import *

# Configuration
TWITTERHANDLE = 'AstroGoldStars'
LOGFILE = 'bot.log'
STREAMING_LOGFILE = 'streaming.log'


class TweetHandler():
    def __init__(self, tweet, dbfile=DEFAULT_DB):
        self.tweet = tweet
        self.dbfile = dbfile
        self.db = GoldStarDB(self.dbfile)

    def handle(self):
        """Save stars to the database and tweet the responses."""
        self.save_to_db()
        self.tweet_responses()

    def get_recipients(self):
        """Returns the recipients of the star as a list of dictionaries."""
        recipients = []
        for mention in self.tweet['entities']['user_mentions']:
            if mention['name'] == TWITTERHANDLE:
                continue
            if self.tweet['text'][mention['indices'][1]] == '+':
                recipients.append(mention)
        return recipients

    def save_to_db(self):
        for recipient in self.get_recipients():
            self.db.add(donor=self.tweet['user'],
                        recipient=recipient,
                        tweet=self.tweet)

    def generate_responses(self):
        responses = []
        for recipient in self.get_recipients():
            url = 'https://twitter.com/{}/status/{}'.format(self.tweet['user']['screen_name'], self.tweet['id'])
            text = ('@{} Congratulations, '
                    'you just earned a 🌟 from @{}! Your total is {}. '
                    '{}'.format(
                            recipient['screen_name'],
                            self.tweet['user']['screen_name'],
                            self.db.count_stars(recipient['id']),
                            url))
            responses.append(text)
        return responses

    def tweet_responses(self):
        twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        for response in self.generate_responses():
            result = twitter.update_status(status=response,
                                           in_reply_to_status_id=self.tweet['id'])
            with open(LOGFILE, 'a') as log:
                log.write(result)
        return twitter, result


class GoldStarStreamer(TwythonStreamer):

    def __init__(self):
        super(GoldStarStreamer, self).__init__(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    def on_success(self, data):
        try:
            with open(STREAMING_LOGFILE, 'a') as log:
                log.write(json.dumps(data))
            if 'text' in data and data['user']['screen_name'] != TWITTERHANDLE:
                handler = TweetHandler(data)
                handler.handle()
        except Exception as e:
            print('ERROR! {}'.format(e))

    def on_error(self, status_code, data):
        print('ERROR: {}'.format(status_code))


def run():
    stream = GoldStarStreamer()
    stream.statuses.filter(track='@'+TWITTERHANDLE)


if __name__ == '__main__':
    run()
