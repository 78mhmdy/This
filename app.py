import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# إعداد Firebase
cred = credentials.Certificate("path_to_your_firebase_credentials.json")
firebase_admin.initialize_app(cred)

# الاتصال بقاعدة بيانات Firestore
db = firestore.client()

# واجهة المستخدم باستخدام Streamlit
st.title('تطبيق تواصل اجتماعي باستخدام Firebase')

menu = ['تسجيل الدخول', 'تسجيل حساب']
choice = st.sidebar.selectbox("اختر العملية", menu)

# تسجيل الحساب
if choice == 'تسجيل حساب':
    st.subheader("إنشاء حساب")
    username = st.text_input('اسم المستخدم')
    password = st.text_input('كلمة المرور', type='password')

    if st.button("تسجيل"):
        if username and password:
            # حفظ البيانات في Firebase
            user_ref = db.collection('users').document(username)
            user_ref.set({
                'username': username,
                'password': password
            })
            st.success("تم تسجيل الحساب بنجاح!")
        else:
            st.error("الرجاء إدخال جميع البيانات.")

# تسجيل الدخول
elif choice == 'تسجيل الدخول':
    st.subheader("تسجيل الدخول")
    username = st.text_input('اسم المستخدم')
    password = st.text_input('كلمة المرور', type='password')

    if st.button("تسجيل الدخول"):
        # التحقق من المستخدم في Firebase
        user_ref = db.collection('users').document(username)
        user = user_ref.get()
        if user.exists:
            user_data = user.to_dict()
            if user_data['password'] == password:
                st.success(f"مرحبًا {username}!")
            else:
                st.error("كلمة المرور غير صحيحة.")
        else:
            st.error("اسم المستخدم غير موجود.")
