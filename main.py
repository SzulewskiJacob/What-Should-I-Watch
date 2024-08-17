import streamlit as st
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('OPENAI_KEY'),
)

st.title("What Should I Watch?")

genres = st.text_input("Which genres interest you?", placeholder='horror, but less jump scares')
streaming_services = st.text_input("Which streaming services do you have access to?", placeholder="Max, Hulu")
content_type = st.selectbox(
    "Movies, shows, or both?",
    ["TV Shows", "Movies", "Both"]
)
additional_info = st.text_area("Anything else you'd like to share?", placeholder='Ideally something made in the last 10 years. I like A24 movies.')

if st.button("Get Recommendation"):
    genre_str = genres if genres != '' else "any"
    streaming_service_str = streaming_services if streaming_services != "" else "any streaming service"
    content_type_str = content_type if content_type in ('TV Shows','Movies') else "TV shows or movies"
    
    prompt = f"I like {genre_str} {content_type_str} and I have access to {streaming_service_str}. {additional_info}. Please provide 4 options on what I should watch."
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "You are a helpful assistant. " + prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )   
    st.write(chat_completion.choices[0].message.content)
