from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback

app = Flask(__name__)
CORS(app)

# Simple dictionary for rewriting common terms
REWRITE_MAP = {
    'flask': 'Flask (Python web framework)',
    'react': 'React (JavaScript UI library)',
    'node': 'Node.js runtime',
    'django': 'Django (Python web framework)'
}

@app.route('/api/rewrite', methods=['POST'])
def rewrite_text():
    data = request.get_json(force=True)
    text = data.get('text', '')
    rewritten = ' '.join(REWRITE_MAP.get(word.lower(), word) for word in text.split())
    return jsonify({'rewritten': rewritten})

@app.route('/api/clarify')
def clarify_concept():
    concept = request.args.get('concept', '')
    if not concept:
        return jsonify({'error': 'Missing concept'}), 400
    try:
        url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + concept
        resp = requests.get(url, timeout=5)
        if resp.ok:
            data = resp.json()
            summary = data.get('extract', 'No summary found.')
            return jsonify({'summary': summary})
    except Exception:
        traceback.print_exc()
    return jsonify({'error': 'Could not fetch clarification.'}), 500

@app.route('/api/answer')
def answer_question():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Missing query'}), 400
    try:
        params = {
            'order': 'desc',
            'sort': 'relevance',
            'accepted': 'True',
            'site': 'stackoverflow',
            'title': query,
            'filter': 'withbody',
            'pagesize': 1
        }
        resp = requests.get('https://api.stackexchange.com/2.3/search/advanced', params=params, timeout=5)
        if resp.ok:
            data = resp.json()
            if data.get('items'):
                item = data['items'][0]
                answer = {
                    'title': item.get('title'),
                    'link': item.get('link')
                }
                return jsonify({'answer': answer})
    except Exception:
        traceback.print_exc()
    return jsonify({'error': 'Could not fetch answer.'}), 500

@app.route('/api/debug', methods=['POST'])
def debug_code():
    data = request.get_json(force=True)
    code = data.get('code', '')
    try:
        compile(code, '<string>', 'exec')
        return jsonify({'result': 'No syntax errors detected.'})
    except SyntaxError as e:
        return jsonify({'result': f'Syntax error: {e}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
