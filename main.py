from flask import Flask, request
from flask_cors import CORS
from googletrans import Translator
import os
import re

app = Flask(__name__)
app.debug = True
CORS(app)

translator = Translator()

@app.route('/scripts')
def get_scripts():
    search = request.args.get('words').split(',')
    limit = 5
    if 'limit' in request.args:
        limit = int(request.args.get('limit'))
    results = {}
    for word in search:
        results[word] = {}
    
    for filename in os.listdir('scripts'):
        game_name = filename[:-4]
        with open(os.path.join('scripts', filename)) as script_file:
            total_results_so_far = 0
            linenum = 1
            for voiceline in script_file:
                if total_results_so_far >= limit:
                    break
                for stem in search:
                    colon_index = voiceline.find(':')
                    speaker = voiceline[:colon_index].strip()
                    quote = voiceline[colon_index + 1:].strip()
                    newquote, found = re.compile(r'\b(' + re.escape(stem) + r')\b', re.IGNORECASE).subn('{qword}\\1{/qword}', quote)
                    if found != 0:
                        if not game_name in results[stem]:
                            results[stem][game_name] = []
                        results[stem][game_name].append({ 'speaker': speaker, 'quote': newquote, 'id': game_name + '-' + str(linenum) })
                        total_results_so_far += 1
                linenum += 1
    return results

@app.route('/games')
def get_games():
    result = []
    
    for filename in os.listdir('scripts'):
        game_name = filename[:-4]
        result.append(game_name)
    return { 'games': result }
    
@app.route('/translate')
def get_translation():
    search = request.args.get('words').split(',')
    results = {}

    for translation in translator.translate(search, dest='bn'):
        results[translation.origin] = { 'direct': translation.text, 'pronunciation': translation.pronunciation }
    
    return results

if __name__ == '__main__':
   app.run(threaded = True)