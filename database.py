import sqlite3

def create_db():
    conn = sqlite3.connect('social_media.db')
    c = conn.cursor()

    # إنشاء جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')

    # إنشاء جدول التغريدات
    c.execute('''CREATE TABLE IF NOT EXISTS tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id))''')

    # إنشاء جدول الإعجابات
    c.execute('''CREATE TABLE IF NOT EXISTS likes (
                    tweet_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (tweet_id, user_id),
                    FOREIGN KEY (tweet_id) REFERENCES tweets (id),
                    FOREIGN KEY (user_id) REFERENCES users (id))''')

    conn.commit()
    conn.close()

create_db()
