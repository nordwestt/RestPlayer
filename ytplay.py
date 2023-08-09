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
    print("returning!")
    return send_file("static/ai-plugin.json")

def play_song():
    global is_playing, current_process
    while True:
        
        while current_process != None and current_process.wait():
            time.sleep(0.1)
        
        song = song_queue.get(block=True)
        current_process = subprocess.Popen(f'yt-dlp -f bestaudio ytsearch:"{song}" -o - | mpv -', shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
        
        # if song and current_process == None:
        #     print(f"Playing song {song}")
        #     # Download and play the song using yt-dlp and a media player (e.g., mpv)
        #     current_process = subprocess.Popen(f'yt-dlp -f bestaudio ytsearch:"{song}" -o - | mpv -', shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
            
        #     #return_code = subprocess.call(["yt-dlp", "-f", "bestaudio", f'ytsearch:{song}', "-o", "-", "|", "mpv", "-"], shell=True)
        #     # Instead of waiting indefinitely, periodically check if the process is still running
        #     #while current_process != None:  # While the process is still running
        #     #    if not song_queue.empty():  # If there's a new song in the queue
        #     #        current_process.terminate()  # Terminate the current song
        #     #        break  # Break out of the loop to start the next song
        #     #    time.sleep(1)  # Sleep for a short duration before checking again
        #     #print("exited process!!")
        #     #current_process.wait()
        # time.sleep(0.1)

@app.route('/stop_song', methods=['POST'])
@cross_origin()
def stop_song():
    global current_process
    if current_process != None:
        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        #current_process.terminate()
        current_process = None
        print("stopped process")
    return jsonify({"message": "Song stopped!"}), 200

@app.route('/add_song', methods=['POST'])
@cross_origin()
def add_song():
    song_name = request.json.get('song_name')
    if song_name:
        song_queue.put(song_name)
        print("added song")
        return jsonify({"message": "Song added to queue!"}), 200
    return jsonify({"message": "Song name not provided!"}), 400

@app.route('/play_now', methods=['POST'])
@cross_origin()
def play_now():
    global current_process
    song_name = request.json.get('song_name')
    if song_name:
        if current_process != None:
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            #current_process.terminate()
            current_process = None
        # Clear the queue and play the song immediately
        while not song_queue.empty():
            song_queue.get()
        song_queue.put(song_name)
        return jsonify({"message": "Song will play now!"}), 200
    return jsonify({"message": "Song name not provided!"}), 400

@app.route('/clear_queue', methods=['POST'])
@cross_origin()
def clear_queue():
    while not song_queue.empty():
        song_queue.get()
    return jsonify({"message": "Queue cleared!"}), 200

threading.Thread(target=play_song, daemon=True).start()

if __name__ == '__main__':
    # Start the song playing thread
    threading.Thread(target=play_song).start()
    app.run(port=5000)
