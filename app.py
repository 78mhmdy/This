import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import Session, DeclarativeBase
import telegram
from telegram.error import InvalidToken

class Base(DeclarativeBase):
    pass

class BotConfig(Base):
    __tablename__ = 'bot_config'
    
    id = Column(Integer, primary_key=True)
    bot_token = Column(String, nullable=False)
    source_chat_id = Column(String)
    target_chat_id = Column(String)
    is_active = Column(Boolean, default=False)

# Create database and tables
engine = create_engine('sqlite:///telegram_forwarder.db')
Base.metadata.create_all(engine)

st.title('Telegram Message Forwarder')

def validate_token(token):
    try:
        bot = telegram.Bot(token=token)
        bot.get_me()
        return True
    except InvalidToken:
        return False
    except Exception as e:
        st.error(f"Error validating token: {str(e)}")
        return False

# Initialize session state
if 'bot_configured' not in st.session_state:
    st.session_state.bot_configured = False

# Get existing configuration
with Session(engine) as session:
    config = session.query(BotConfig).first()
    if config:
        st.session_state.bot_configured = True

# Bot Configuration Section
st.header('Bot Configuration')

with st.form('bot_config'):
    token = st.text_input('Bot Token', value=config.bot_token if config else '', type='password')
    source_id = st.text_input('Source Chat ID', value=config.source_chat_id if config else '',
                             help='The chat ID from which messages will be forwarded')
    target_id = st.text_input('Target Chat ID', value=config.target_chat_id if config else '',
                             help='The chat ID to which messages will be forwarded')
    
    submit = st.form_submit_button('Save Configuration')
    
    if submit:
        if not token:
            st.error('Bot token is required')
        elif not validate_token(token):
            st.error('Invalid bot token')
        else:
            with Session(engine) as session:
                if config:
                    config.bot_token = token
                    config.source_chat_id = source_id
                    config.target_chat_id = target_id
                else:
                    new_config = BotConfig(
                        bot_token=token,
                        source_chat_id=source_id,
                        target_chat_id=target_id
                    )
                    session.add(new_config)
                session.commit()
            st.success('Configuration saved successfully!')
            st.toast('Bot configuration updated!', icon='✅')
            st.session_state.bot_configured = True
            st.rerun()

# Bot Control Section
if st.session_state.bot_configured:
    st.header('Bot Control')
    
    with Session(engine) as session:
        config = session.query(BotConfig).first()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button('Test Connection'):
                try:
                    bot = telegram.Bot(token=config.bot_token)
                    bot_info = bot.get_me()
                    st.success(f'Connected to bot: {bot_info.first_name} (@{bot_info.username})')
                except Exception as e:
                    st.error(f'Error connecting to bot: {str(e)}')
        
        with col2:
            if st.button('Toggle Bot', type='primary'):
                config.is_active = not config.is_active
                session.commit()
                status = 'activated' if config.is_active else 'deactivated'
                st.success(f'Bot {status} successfully!')
                st.toast(f'Bot {status}!', icon='🤖')
    
    # Display current status
    st.info(f"Bot is currently {'active' if config.is_active else 'inactive'}")
    
    # Instructions
    st.header('Instructions')
    st.markdown("""
    1. Create a new bot using [@BotFather](https://t.me/botfather) on Telegram
    2. Copy the bot token and paste it in the configuration above
    3. Add the bot to both source and target groups
    4. Make the bot an admin in both groups
    5. Get the chat IDs and configure them above
    6. Toggle the bot to start forwarding messages
    
    **Note:** To get a chat ID, you can:
    - Forward a message from the group to [@getidsbot](https://t.me/getidsbot)
    - Or use the format `-100xxx` for public groups/channels
    """)

# Warning about security
st.sidebar.warning("""
⚠️ **Security Notice**

Keep your bot token secure and never share it with others.
The token provides full access to your bot.
""")

# About section in sidebar
st.sidebar.info("""
### About Telegram Forwarder

This bot helps you automatically forward messages from one chat to another.
Perfect for:
- Content syndication
- Channel management
- Cross-posting between groups
""")