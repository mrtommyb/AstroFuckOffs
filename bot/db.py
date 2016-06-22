"""Wraps the sqlite database of @AstroGoldStarz"""
import json
import os
import sqlite3 as sql

DEFAULT_DB = os.path.expanduser("~/.goldstar.db")


class GoldStarDB():
    """Class wrapping the SQLite database for @AstroGoldStarz on twitter.

    Parameters
    ----------
    filename : str
        Path to the SQLite database file.
    """
    def __init__(self, filename=DEFAULT_DB):
        self.filename = filename
        self.con = sql.connect(filename)
        pubs_table_exists = self.con.execute(
                                """
                                   SELECT COUNT(*) FROM sqlite_master
                                   WHERE type='table' AND name IN ('stars', 'transactions');
                                """).fetchone()[0]
        if not pubs_table_exists:
            self.create_tables()

    def create_tables(self):
        #self.con.execute("""CREATE TABLE stars(
        #                        user_id,
        #                        user_handle,
        #                        stars,
        #                        last_update DATETIME);""")
        self.con.execute("""CREATE TABLE transactions(
                                status_id,
                                time DATETIME,
                                donor_id,
                                donor_handle,
                                recipient_id,
                                recipient_handle,
                                tweet);""")

    def add(self, donor, recipient, tweet):
        cur = self.con.execute("INSERT INTO transactions "
                               "VALUES (?, ?, ?, ?, ?, ?, ?)",
                               [tweet['id'],
                                tweet['created_at'],
                                donor['id'],
                                donor['screen_name'],
                                recipient['id'],
                                recipient['screen_name'],
                                json.dumps(tweet)])
        #print('Inserted {} row(s).'.format(cur.rowcount))
        self.con.commit()

    def count_stars(self, user_id):
        stars = self.con.execute(
                                """
                                   SELECT COUNT(*)
                                   FROM transactions
                                   WHERE recipient_id = ?;
                                """, [user_id]).fetchone()[0]
        return stars

if __name__ == '__main__':
    db = GoldStarDB()
