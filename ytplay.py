from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
import subprocess
import threading
import queue
import time
import os
import signal

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Queue to hold song names
song_queue = queue.Queue()

# Flag to check if a song is currently playing
is_playing = False
current_process = None


@app.route('/.well-known/ai-plugin.json', methods=['GET'])
@cross_origin()
def aiPlugin():
    return send_file("static/ai-plugin.json")

def play_song():
    global is_playing, current_process
    while True:
        
        while current_process != None and current_process.wait():
            time.sleep(0.1)
        
        song = song_queue.get(block=True)
        current_process = subprocess.Popen(f'yt-dlp -f bestaudio ytsearch:"{song}" -o - | mpv -', shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
        
       
@app.route('/stop_playback', methods=['POST'])
@cross_origin()
def stop_playback():
    global current_process
    if current_process != None:
        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        current_process = None
        print("Stopped playback")
    return jsonify({"message": "Song stopped!"}), 200

@app.route('/queue_songs', methods=['POST'])
@cross_origin()
def queue_songs():
    song_names = request.json.get('song_names')
    if song_names:
        for song_name in song_names:
            song_queue.put(song_name)

        print("\Queued songs\n")
        return jsonify({"message": "Song added to queue!"}), 200
    return jsonify({"message": "Song names not provided!"}), 400

@app.route('/play_songs', methods=['POST'])
@cross_origin()
def play_songs():
    global current_process
    song_names = request.json.get('song_names')
    if song_names:
        if current_process != None:
            try:
                os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            except:
                pass
            current_process = None

        # Clear the queue
        while not song_queue.empty():
            song_queue.get()

        for song_name in song_names:
            song_queue.put(song_name)
        
        print("Playing songs")
        return jsonify({"message": "Song will play now!"}), 200
    return jsonify({"message": "Song name not provided!"}), 400

@app.route('/clear_queue', methods=['POST'])
@cross_origin()
def clear_queue():
    while not song_queue.empty():
        song_queue.get()
    print("Queue cleared")
    return jsonify({"message": "Queue cleared!"}), 200


if __name__ == '__main__':
    # Start the song playing thread
    threading.Thread(target=play_song).start()
    app.run(port=5000)
else:
    threading.Thread(target=play_song, daemon=True).start()
