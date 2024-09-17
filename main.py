import streamlit as st
from openai import OpenAI
import os
import requests
import re

client = OpenAI(
    api_key=st.secrets['OPENAI_KEY'],
)

def get_movie_details(title):
    print(title)
    omdb_api_key = st.secrets['OMDB_KEY']
    params = {
        't': title,
        'apikey': omdb_api_key,
        'plot': 'short'
    }
    response = requests.get('https://www.omdbapi.com/', params=params)
    data = response.json()
    if response.status_code == 200 and data.get('Response') == 'True':
        cover_url = data.get('Poster')
        rotten_score = None
        for rating in data.get('Ratings', []):
            print(rating['Source'])
            print(rating['Value'])
            if rating['Source'] == 'Internet Movie Database':
                rotten_score = rating['Value']
                break
        # Fetch image data
        cover_data = None
        if cover_url and cover_url != 'N/A':
            try:
                image_response = requests.get(cover_url)
                if image_response.status_code == 200:
                    cover_data = image_response.content
            except Exception as e:
                print(f"Error fetching image: {e}")
        return cover_data, rotten_score
    else:
        return None, None

def parse_openai_response(response_text):
    # Regex to match individual recommendations
    pattern = r'\d+\.\s"([^"]+)"\son\s([^\s]+)\s-\s(.+?)$'
    
    # Split the response into lines for easier manipulation
    lines = response_text.strip().split('\n')
    
    # Find the first line that matches the recommendation pattern
    start_idx = next((i for i, line in enumerate(lines) if re.match(pattern, line)), None)
    # Find the last line that matches the recommendation pattern
    end_idx = next((i for i in reversed(range(len(lines))) if re.match(pattern, lines[i])), None)
    
    # Extract preamble, recommendations, and postamble
    preamble = "\n".join(lines[:start_idx]).strip()
    recommendations_text = "\n".join(lines[start_idx:end_idx+1]).strip()
    postamble = "\n".join(lines[end_idx+1:]).strip() if end_idx is not None and end_idx + 1 < len(lines) else ""
    
    # Parse the recommendations using regex
    matches = re.findall(pattern, recommendations_text, re.MULTILINE)
    
    parsed_results = []
    for match in matches:
        title, streaming_service, description = match
        parsed_results.append({
            'title': title,
            'streaming_service': streaming_service,
            'description': description
        })
    
    return preamble, parsed_results, postamble

st.title("What Should I Watch")

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
    
    prompt = f"I like {genre_str} {content_type_str} and I have access to {streaming_service_str}. {additional_info}." + ''' 
    Please provide 4 options on what I should watch. Also provide a short witty preamble to the options that marries what I said to the suggestions, 
    and specify which service the titles are on (i.e. 1. "Title" on streaming_service - additional info). Also include a light postamble. 
    Don't use any asterisks in response. Make sure the streaming service is only one word, so you can just say Prime or Max. And confirm that the 
    streaming platform is one of the ones I mentioned in the beginning of this request. Also please make sure you provide the additional info on each title.'''
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "You are a helpful assistant. " + prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )   
    response_text = chat_completion.choices[0].message.content.replace('HBO Max','Max')
    print(response_text)
    preamble, parsed_results, postamble = parse_openai_response(response_text)
    st.write('')
    st.markdown('---')
    st.write('')
    # Display the preamble
    st.write(preamble)
    st.write('')
    # Display each recommendation with cover art and IMDB score
    for result in parsed_results:
        title = result['title']
        description = result['description']
        service = result['streaming_service']
        cover_data, rotten_score = get_movie_details(title)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if cover_data:
                st.image(cover_data, width=100)
            else:
                st.text("Cover art not found")
        with col2:
            st.subheader(title)
            if rotten_score:
                st.text(f"{service} - IMDB Score: {rotten_score}")
            else:
                st.text(f"{service} - IMDB Score: Not available")
            st.write(description)
    st.write('')
    # Display the postamble
    st.write(postamble)
