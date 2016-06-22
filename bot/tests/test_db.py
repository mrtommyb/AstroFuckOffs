import os

from .. import bot
from .. import db

from .test_bot import EXAMPLE_TWEET

TESTDB = 'test_goldstar.db'


class TestDB():

    def setup(self):
        os.remove(TESTDB)
        self.db = db.GoldStarDB(TESTDB)

    def teardown(self):
        os.remove(TESTDB)

    def test_db_save(self):
        # Save a tweet to the test db and check if it got inserted
        handler = bot.TweetHandler(EXAMPLE_TWEET, dbfile=TESTDB)
        handler.save_to_db()
        for recipient in handler.get_recipients():
            assert self.db.count_stars(recipient['id']) == 1
        assert self.db.count_stars(123) == 0  # Random user_id
