import streamlit as st
from openai import OpenAI
import os
import requests
import re

client = OpenAI(
    api_key=os.getenv('OPENAI_KEY'),
)

def get_movie_details(title):
    omdb_api_key = os.getenv('OMDB_KEY')
    params = {
        't': title,
        'apikey': omdb_api_key,
        'plot': 'short'
    }
    response = requests.get('http://www.omdbapi.com/', params=params)
    data = response.json()
    if response.status_code == 200 and data.get('Response') == 'True':
        cover_url = data.get('Poster')
        rotten_score = None
        for rating in data.get('Ratings', []):
            if rating['Source'] == 'Rotten Tomatoes':
                rotten_score = rating['Value']
                break
        return cover_url, rotten_score
    else:
        return None, None
    
def parse_openai_response(response_text):
    pattern = r'\d+\.\s"([^"]+)"\son\s([^\s]+)\s-\s(.+?)$'
    matches = re.findall(pattern, response_text, re.MULTILINE)
    parsed_results = []
    for match in matches:
        title, streaming_service, description = match
        parsed_results.append({
            'title': title,
            'streaming_service': streaming_service,
            'description': description
        })
    return parsed_results

st.title("What Should I Watch?")

genres = st.text_input("Which genres interest you?", placeholder='Thriller, Horror, but less jump scares')
streaming_services = st.text_input("Which streaming services do you have access to?", placeholder="Max, Hulu")
content_type = st.selectbox(
    "Movies, shows, or both?",
    ["Both", "TV Shows", "Movies"]
)
additional_info = st.text_area("Anything else you'd like to share?", placeholder='Ideally something made in the last 10 years. I like A24 movies.')

if st.button("Get Recommendation"):
    genre_str = genres if genres != '' else "any"
    streaming_service_str = streaming_services if streaming_services != "" else "any streaming service"
    content_type_str = content_type if content_type in ('TV Shows','Movies') else "TV shows or movies"
    
    prompt = f"I like {genre_str} {content_type_str} and I have access to {streaming_service_str}. {additional_info}. Please provide 4 options on what I should watch. Also provide a short witty preamble to the options that marries what I said to the suggestions."
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "You are a helpful assistant. " + prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )   
    response_text = chat_completion.choices[0].message.content
    parsed_results = parse_openai_response(response_text)

    # Display each recommendation with cover art and Rotten Tomatoes score
    for result in parsed_results:
        title = result['title']
        description = result['description']
        cover_url, rotten_score = get_movie_details(title)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if cover_url:
                st.image(cover_url, width=100)
            else:
                st.text("Cover art not found")
        with col2:
            st.subheader(title)
            if rotten_score:
                st.text(f"Rotten Tomatoes Score: {rotten_score}")
            else:
                st.text("Rotten Tomatoes Score: Not available")
            st.write(description)