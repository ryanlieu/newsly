from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/post/<path:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return post_id