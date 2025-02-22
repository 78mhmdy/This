import streamlit as st
from telethon import TelegramClient, events
import asyncio

# إعداد بيانات API الخاصة بـ Telegram
API_ID = "25140031"
API_HASH = "a9308e99598c9eee9889a1badf2ddd2f"
SESSION_NAME = "forward_bot_session"

# إنشاء جلسة Telethon
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

def login(phone_number):
    """ تسجيل الدخول باستخدام رقم الهاتف """
    async def auth():
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            return True
        return False
    return asyncio.run(auth())

def verify_code(phone_number, code):
    """ التحقق من كود OTP """
    async def auth():
        await client.sign_in(phone_number, code)
    asyncio.run(auth())

# واجهة Streamlit
st.title("بوت تحويل الرسائل بين القنوات")

phone_number = st.text_input("أدخل رقم هاتفك مع الكود الدولي")
if st.button("تسجيل الدخول"):
    if login(phone_number):
        st.session_state["phone"] = phone_number
        st.success("تم إرسال كود التحقق، أدخله في الأسفل")

code = st.text_input("أدخل كود التحقق")
if st.button("تحقق"):
    verify_code(st.session_state["phone"], code)
    st.success("تم تسجيل الدخول بنجاح")

# اختيار القنوات
if client.is_connected():
    source_channel = st.text_input("أدخل معرف القناة المصدر (مثل @source_channel)")
    target_channel = st.text_input("أدخل معرف القناة الهدف (مثل @target_channel)")
    
    if st.button("ابدأ التحويل"):
        async def forward_messages():
            @client.on(events.NewMessage(chats=source_channel))
            async def handler(event):
                await client.send_message(target_channel, event.message)
                
            await client.run_until_disconnected()
        
        st.success("بدأ تحويل الرسائل!")
        asyncio.run(forward_messages())

# تشغيل Streamlit عبر: streamlit run script.py
