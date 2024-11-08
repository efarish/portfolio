#!/usr/bin/env python
import logging
import os

from dotenv import load_dotenv
from flask import Flask, request

app = Flask(__name__)

load_dotenv()

@app.route('/')
def do_request() -> str:
    msg = request.args.get("msg","")
    if len( msg ) == 0:
        return "No message provided."
    else:
        logging.info(f'Submitted: {msg}')

    return f' \nMessage received - {msg}.'
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 9090), debug=True)