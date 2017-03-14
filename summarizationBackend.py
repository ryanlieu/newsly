from backendSummarization import getArticleTitleText, extractSentences
from flask import Flask
from flask import jsonify
from flask_cors import CORS, cross_origin
import os 
app = Flask(__name__)
CORS(app)

@app.route('/')
@cross_origin()
def home():
    """Render website's home page."""
    return "USAGE: /summarize/length/url"

@app.route('/summarize/<int:numSentences>/<path:summarize_url>/', , methods=['GET'])
@cross_origin()
def show_post(numSentences, summarize_url):
    # show the post with the given id, the id is an integer
    url = summarize_url
    sumText = getArticleTitleText(url)
    return jsonify(title = sumText[0], summary = extractSentences(sumText[1], numSentences))

if __name__ == '__main__':
	app.debug = True
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)