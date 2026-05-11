import streamlit as st
from textblob import TextBlob
import pandas as pd
import ollama

# here is a header part ------------
st.markdown("""
<div style="text-align:center; padding:15px; border-radius:10px; background-color:#f5f5f5; color:#333;">
    <h1>🧠 AI Mental Health Chatbot</h1>
    <p>Created by <b>Anushtha, Aryan, Harsh, and Hardik</b></p>
    <p>Talk to your AI companion and track your mood over time!</p>
</div>
""", unsafe_allow_html=True)


if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'mood_tracker' not in st.session_state:
    st.session_state['mood_tracker'] = []
if 'last_coping_strategy' not in st.session_state:
    st.session_state['last_coping_strategy'] = None

#ollama part---
def generate_response(prompt):
    try:
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

#graphical part 
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.5:
        return "Very Positive", polarity
    elif 0.1 < polarity <= 0.5:
        return "Positive", polarity
    elif -0.1 <= polarity <= 0.1:
        return "Neutral", polarity
    elif -0.5 < polarity < -0.1:
        return "Negative", polarity
    else:
        return "Very Negative", polarity


def provide_coping_strategy(sentiment):
    strategies = {
        "Very Positive": "Keep up the positive vibes! 🌟",
        "Positive": "Great to see you're feeling good! 😊",
        "Neutral": "Try doing something you enjoy today. 🎯",
        "Negative": "Take a break, relax, and breathe deeply. 🌿",
        "Very Negative": "Please consider talking to someone you trust. 💙"
    }
    return strategies.get(sentiment, "Stay strong!")


with st.form(key='chat_form'):
    user_message = st.text_input("Type your message here...")
    submit_button = st.form_submit_button("Send")

if submit_button and user_message:
    st.session_state['messages'].append(("You", user_message))
    sentiment, polarity = analyze_sentiment(user_message)
    coping_strategy = provide_coping_strategy(sentiment)
    st.session_state['last_coping_strategy'] = coping_strategy

    with st.spinner("🤖 Bot is thinking..."):
        response = generate_response(user_message)

    st.session_state['messages'].append(("Bot", response))
    st.session_state['mood_tracker'].append((user_message, sentiment, round(polarity, 2)))

#display chats here 
for sender, message in st.session_state['messages']:
    if sender == "You":
        st.markdown(f"""
        <div style='text-align:right; background-color:#343a40; color:#FFFFFF; 
                    padding:10px; border-radius:12px; margin:5px 0; display:inline-block; max-width:80%'>
            🧑USER {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='text-align:left; background-color:#343a40; color:#FFFFFF; 
                    padding:10px; border-radius:12px; margin:5px 0; display:inline-block; max-width:80%'>
            🤖BOT {message}
        </div>
        """, unsafe_allow_html=True)


if st.session_state['last_coping_strategy']:
    st.markdown(f"""
    <div style='border-left: 4px solid #007BFF; background-color:#343a40; padding:10px; border-radius:8px; margin-top:10px;'>
        💡 <b>Suggested Coping Strategy:</b> {st.session_state['last_coping_strategy']}
    </div>
    """, unsafe_allow_html=True)

#mood chart 
if st.session_state['mood_tracker']:
    st.subheader("📊 Your Mood Over Time")
    mood_data = pd.DataFrame(
        st.session_state['mood_tracker'],
        columns=["Message", "Sentiment", "Polarity"]
    )
    st.line_chart(mood_data['Polarity'])

st.sidebar.title("📌 Mental Health Resources")

st.sidebar.write("1. **Tele-MANAS (India Govt Mental Health Helpline):** 14416 or 1-800-891-4416")
st.sidebar.write("2. **KIRAN Mental Health Helpline (Govt of India):** 1800-599-0019")
st.sidebar.write("3. **iCall (TISS):** 9152987821")
st.sidebar.write("4. **Vandrevala Foundation Helpline:** 9999 666 555")

# Session Summary Button
if st.sidebar.button("Show Session Summary"):
    if st.session_state['mood_tracker']:
        st.sidebar.write("### Session Summary")
        for i, (msg, sent, pol) in enumerate(st.session_state['mood_tracker']):
            st.sidebar.write(f"{i+1}. {msg[:30]}... — {sent} ({pol})")
    else:
        st.sidebar.write("No messages yet!")