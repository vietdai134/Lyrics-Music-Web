from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import lyricsgenius
import google.generativeai as genai

# Load .env
load_dotenv()

# Init Flask
app = Flask(__name__)
CORS(app)

# Init Genius
GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")
genius = lyricsgenius.Genius(GENIUS_API_KEY,
                             skip_non_songs=True,
                             excluded_terms=["(Remix)", "(Live)"],
                             remove_section_headers=True)

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/api/lyrics", methods=["GET"])
def get_lyrics():
    song = request.args.get("song")
    artist = request.args.get("artist")

    if not song or not artist:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        result = genius.search_song(song, artist)
        if result and result.lyrics:
            return jsonify({
                "title": result.title,
                "artist": result.artist,
                "lyrics": result.lyrics
            })
        else:
            return jsonify({"error": "Lyrics not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/translate", methods=["POST"])
def translate_text():
    data = request.get_json()
    text = data.get("text")
    target_language = data.get("target_language", "Vietnamese")

    if not text:
        return jsonify({"error": "Missing text parameter"}), 400

    try:
        prompt = f"Translate the following song lyrics to {target_language}, keeping the tone and style natural:\n\n{text}"
        response = gemini_model.generate_content(prompt)
        return jsonify({"translated_text": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
