import os
import random
import requests
from io import BytesIO
from PIL import Image, ImageSequence
from flask import Flask, request, redirect, url_for, render_template
from my_script import run

app = Flask(__name__)

@app.route('/')
def index():
    return '''
        <form action="/process" method="POST">
            <label for="entry">Type something:</label>
            <input type="text" id="entry" name="entry">
            <button type="submit">Submit</button>
        </form>
    '''

@app.route('/process', methods=['POST'])
def process():
    entry = request.form['entry']
    result = run(entry)
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
    
import sys
print(sys.version)