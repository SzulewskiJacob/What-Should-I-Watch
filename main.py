import streamlit as st
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('OPENAI_KEY'),
)

st.title("What Should I Watch?")

# Multiselect options for genres
genres = st.multiselect(
    "Select your favorite genres",
    ["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Fantasy", "Documentary", "Thriller", "Animation"]
)

# Multiselect options for streaming services
streaming_services = st.multiselect(
    "Which streaming services do you have access to?",
    ["Netflix", "Hulu", "Amazon Prime Video", "Disney+", "HBO Max", "Apple TV+", "Peacock", "Paramount+", "YouTube"]
)

# Multiselect for TV or Movie preference
content_type = st.multiselect(
    "Are you looking for TV shows, movies, or both?",
    ["TV Shows", "Movies", "Both"]
)

# Additional information text area
additional_info = st.text_area("Anything else you'd like to share?")

if st.button("Get Recommendation"):
    # Formatting the prompt with selected options
    genre_str = ", ".join(genres) if genres else "any"
    streaming_service_str = ", ".join(streaming_services) if streaming_services else "any streaming service"
    content_type_str = ", ".join(content_type) if content_type else "TV shows or movies"
    
    prompt = f"I like {genre_str} {content_type_str} and I have access to {streaming_service_str}. {additional_info}. Please help me pick something to watch."
    
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
