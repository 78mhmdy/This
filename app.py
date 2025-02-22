import streamlit as st
from telethon.sync import TelegramClient
import sqlite3
import os

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (phone TEXT PRIMARY KEY, session TEXT)''')
    conn.commit()
    conn.close()

# إعداد Telegram Client
api_id = '25140031'  # استبدلها بـ API ID الخاص بك
api_hash = 'a9308e99598c9eee9889a1badf2ddd2f'  # استبدلها بـ API Hash الخاص بك

# صفحة تسجيل الدخول
def login_page():
    st.title("تسجيل الدخول إلى البوت")
    phone = st.text_input("أدخل رقم هاتفك (مثال: +1234567890)")
    
    if st.button("تسجيل الدخول"):
        if phone:
            client = TelegramClient(phone, api_id, api_hash)
            client.connect()
            if not client.is_user_authorized():
                st.write("تم إرسال رمز التحقق إلى رقمك، أدخله أدناه")
                code = st.text_input("أدخل رمز التحقق")
                if st.button("تحقق"):
                    try:
                        client.sign_in(phone, code)
                        st.success("تم تسجيل الدخول بنجاح!")
                        # حفظ الجلسة في قاعدة البيانات
                        conn = sqlite3.connect('users.db')
                        c = conn.cursor()
                        c.execute("INSERT OR REPLACE INTO users (phone, session) VALUES (?, ?)", 
                                  (phone, phone + '.session'))
                        conn.commit()
                        conn.close()
                        st.session_state['logged_in'] = True
                        st.session_state['phone'] = phone
                    except Exception as e:
                        st.error(f"حدث خطأ: {e}")
            else:
                st.session_state['logged_in'] = True
                st.session_state['phone'] = phone
                st.success("تم تسجيل الدخول بنجاح!")
            client.disconnect()
        else:
            st.error("يرجى إدخال رقم هاتف")

# صفحة تحديد القنوات وتحويل الرسائل
def main_page():
    st.title("بوت تحويل الرسائل")
    phone = st.session_state['phone']
    
    client = TelegramClient(phone, api_id, api_hash)
    client.connect()
    
    # الحصول على قائمة القنوات
    channels = []
    for dialog in client.get_dialogs():
        if dialog.is_channel:
            channels.append((dialog.title, dialog.id))
    
    source_channel = st.selectbox("اختر القناة المصدر", [ch[0] for ch in channels])
    target_channel = st.selectbox("اختر القناة الهدف", [ch[0] for ch in channels])
    
    if st.button("بدء التحويل"):
        source_id = next(ch[1] for ch in channels if ch[0] == source_channel)
        target_id = next(ch[1] for ch in channels if ch[0] == target_channel)
        
        st.write("جاري تحويل الرسائل...")
        for message in client.iter_messages(source_id, limit=10):  # حد 10 رسائل كمثال
            client.send_message(target_id, message.text if message.text else "رسالة بدون نص")
        st.success("تم تحويل الرسائل بنجاح!")
    
    client.disconnect()

# التحكم في الصفحات
def main():
    init_db()
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    main()
