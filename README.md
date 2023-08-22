# Rest Player

A restful music player, allowing songs to be queued and played through HTTP calls. 

> *Can be used as a ChatGPT plugin*

## Description 

Currently only compatible with Linux, this player takes advantage of the Python yt-dlp package to search for and stream songs from YouTube. 
It has a simple queue, which can be added to, skipped through and cleared through the use of HTTP calls. 

Please read the [OpenAPI documentation](static/openapi.yaml) to see how to integrate this into your own application.

## Installation

pip install -r requirements.txt

## Running (as a ChatGPT plugin)

Open a terminal and run:
> flask --app ytplay.py --debug run --host 0.0.0.0

Then, 
- open up ChatGPT 
- navigate to the plugin store
- click 'Develop your own plugin' in the bottom right
- in the field type in 'localhost:5000' and hit 'Find manifest file'

You should see the plugin showing up as an option in ChatGPT now.

## Using it (through ChatGPT)

Simply tell chatgpt to put on a song of your liking or songs of a certain mood, get creative! You can also tell it to stop playback, skip songs or clear the queue out. 

Example prompts:

- "I really like the steadfast beat of Stayin Alive. Please play some songs which have a similar solid beat to them"

- "Play some Michael Jackson for me"

- "I love both Rock music and Middle Eastern music, can you play me some music that's a fusion of the two?"

- "I'm tired now. Please stop the music."




