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

is_paused = False
current_process = None

def endCurrentSong():
    global current_process
    if current_process != None:
        try:
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        except:
            pass
        current_process = None



@app.route('/.well-known/ai-plugin.json', methods=['GET'])
@cross_origin()
def aiPlugin():
    return send_file("static/ai-plugin.json")

def play_song():
    global is_paused, current_process
    while True:
        
        while (current_process != None and current_process.wait()) or is_paused:
            time.sleep(0.1)
        
        song = song_queue.get(block=True)
        current_process = subprocess.Popen(f'yt-dlp -f bestaudio ytsearch:"{song}" -o - | mpv -', shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)    

@app.route('/stop_playback', methods=['POST'])
@cross_origin()
def stop_playback():
    global is_paused

    is_paused = True
    endCurrentSong()
    
    return jsonify({"message": "Song stopped!"}), 200

@app.route('/start_playback', methods=['POST'])
@cross_origin()
def start_playback():
    global is_paused

    is_paused = False
    
    return jsonify({"message": "Playback started!"}), 200

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

        # Clear the queue
        while not song_queue.empty():
            song_queue.get()

        endCurrentSong()

        for song_name in song_names:
            song_queue.put(song_name)
        
        print(f"Playing songs {str(song_names)}")
        
        return jsonify({"message": "Song will play now!"}), 200
    return jsonify({"message": "Song name not provided!"}), 400

@app.route('/skip_songs', methods=['POST'])
@cross_origin()
def skip_songs():
    if song_queue.empty():
        return jsonify({"message": "No songs to skip!"}), 200
    
    number = request.json.get('number')

    if number == None or number <1:
        return jsonify({"message": "No songs to skip!"}), 200
    
    # Pop out songs from queue as required
    for i in range(number-1):
        song_queue.get()

    # Stop playback - will automatically play next 
    endCurrentSong()

    print(f"{number} songs skipped")
    return jsonify({"message": f"{number} song skipped!"}), 200

@app.route('/clear_queue', methods=['POST'])
@cross_origin()
def clear_queue():
    while not song_queue.empty():
        song_queue.get()
    print("Queue cleared")
    return jsonify({"message": "Queue cleared!"}), 200


if __name__ == '__main__':
    # Start the song playing thread
    
    app.run(port=5000)
else:
    threading.Thread(target=play_song, daemon=True).start()

threading.Thread(target=play_song, daemon=True).start()