import sqlite3
from config import *


class DatabaseWorker:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Channels (
                id INTEGER PRIMARY KEY,
                channel TEXT NOT NULL,
                twitter TEXT,
                telegram TEXT,
                instagram TEXT,
                facebook TEXT
            )
        ''')

        self.conn.commit()

    def append_user(self, data):
        channel_name = data['channel_uniqname']
        tg = data['links']['telegram']
        insta = data['links']['instagram']
        fb = data['links']['facebook']
        twitter = data['links']['twitter']

        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO Channels (channel, twitter, telegram, instagram, facebook) VALUES (?, ?, ?, ?, ?)', (
            channel_name,
            twitter,
            tg,
            insta,
            fb
        ))

        self.conn.commit()

    def check_user_exists(self, data):
        channel_name = data['channel_uniqname']
        tg = data['links']['telegram']
        insta = data['links']['instagram']
        fb = data['links']['facebook']
        twitter = data['links']['twitter']

        cursor = self.conn.cursor()

        query = f"SELECT EXISTS (SELECT 1 FROM Channels WHERE channel = ? AND (twitter = ? OR telegram = ? OR instagram = ? OR facebook = ?))"

        cursor.execute(query, (channel_name, twitter, tg, insta, fb))
        result = cursor.fetchone()[0]

        return bool(result)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.close()

