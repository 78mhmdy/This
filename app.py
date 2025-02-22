import streamlit as st
import sqlite3
from hashlib import sha256

# الاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('social_media.db')
    return conn

# وظيفة لتسجيل مستخدم جديد
def register_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        st.success("تم تسجيل الحساب بنجاح!")
    except sqlite3.IntegrityError:
        st.error("اسم المستخدم موجود بالفعل.")
    conn.close()

# وظيفة لتسجيل الدخول
def login_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

# وظيفة لإنشاء تغريدة
def post_tweet(user_id, content):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO tweets (user_id, content) VALUES (?, ?)', (user_id, content))
    conn.commit()
    conn.close()

# وظيفة لإعجاب بتغريدة
def like_tweet(user_id, tweet_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO likes (tweet_id, user_id) VALUES (?, ?)', (tweet_id, user_id))
    conn.commit()
    conn.close()

# واجهة تسجيل الدخول أو التسجيل
st.title('تطبيق تواصل اجتماعي')

menu = ['تسجيل الدخول', 'تسجيل حساب']
choice = st.sidebar.selectbox("اختر العملية", menu)

if choice == 'تسجيل حساب':
    st.subheader("إنشاء حساب")
    username = st.text_input('اسم المستخدم')
    password = st.text_input('كلمة المرور', type='password')

    if st.button("تسجيل"):
        if username and password:
            register_user(username, password)
        else:
            st.error("الرجاء إدخال جميع البيانات.")

elif choice == 'تسجيل الدخول':
    st.subheader("تسجيل الدخول")
    username = st.text_input('اسم المستخدم')
    password = st.text_input('كلمة المرور', type='password')

    if st.button("تسجيل الدخول"):
        user = login_user(username, password)
        if user:
            st.success(f"مرحبًا {username}!")
            user_id = user[0]  # Assuming user ID is the first column
            content = st.text_area("أكتب تغريدتك هنا:")
            if st.button("نشر"):
                if content:
                    post_tweet(user_id, content)
                    st.success("تم نشر التغريدة!")

            # عرض التغريدات
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('SELECT * FROM tweets ORDER BY id DESC')
            tweets = c.fetchall()
            conn.close()

            st.subheader("التغريدات:")
            for tweet in tweets:
                tweet_id, user_id, content = tweet
                st.write(f"تغريدة: {content}")
                st.button("إعجاب", key=tweet_id, on_click=like_tweet, args=(user_id, tweet_id))
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
