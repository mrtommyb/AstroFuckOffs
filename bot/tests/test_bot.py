import json

from .. import bot


EXAMPLE_TWEET = json.load(open('tests/example-tweet.json', 'r'))
TESTDB = 'test_goldstar.db'

def test_recipients():
    handler = bot.TweetHandler(EXAMPLE_TWEET, dbfile=TESTDB)
    recipients = handler.get_recipients()
    assert len(recipients) == 1
    assert recipients[0]['screen_name'] == 'exoplaneteer'


def test_responses():
    handler = bot.TweetHandler(EXAMPLE_TWEET, dbfile=TESTDB)
    handler.save_to_db()
    responses = handler.generate_responses()
    assert len(responses) == 1  # only 1 star handed out
    assert len(responses[0]) < 140  # max tweet length
    assert responses[0] == '@GeertHub @exoplaneteer Congratulations Dan, you just earned a 🌟! Your total is 1.'
