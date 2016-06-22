import os
import json
import pytest

from .. import bot, PACKAGEDIR


EXAMPLE_TWEET = json.load(open(os.path.join(PACKAGEDIR, 'tests', 'examples', 'example-tweet.json'), 'r'))
EXAMPLE_RETWEET = json.load(open(os.path.join(PACKAGEDIR, 'tests', 'examples', 'retweeted-status.json'), 'r'))

TESTDB = 'test_goldstar.db'

def test_recipients():
    handler = bot.TweetHandler(EXAMPLE_TWEET, dbfile=TESTDB, dry_run=True)
    recipients = handler.get_recipients()
    assert len(recipients) == 1
    assert recipients[0]['screen_name'] == 'exoplaneteer'


def test_responses():
    handler = bot.TweetHandler(EXAMPLE_TWEET, dbfile=TESTDB, dry_run=True)
    responses = handler.handle()
    assert len(responses) == 1  # only 1 star handed out
    assert len(responses[0]) < 140  # max tweet length
    assert responses[0] == '@exoplaneteer Congratulations, you just earned a 🌟 from @GeertHub! Your total is 1. https://twitter.com/GeertHub/status/745616020581265408'


def test_retweet():
    """A retweet should not result in a star!"""
    with pytest.raises(bot.InvalidTweetException):
        handler = bot.TweetHandler(EXAMPLE_RETWEET, dbfile=TESTDB, dry_run=True)
