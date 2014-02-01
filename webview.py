#!/usr/bin/env python
"""Raspberry Pi surveillance - web viewer module
Copyright (c) 2014 Patrick Van Oosterwijck
Distributed under GPL v2 license"""

from flask import *
import os
import os.path
import zipfile

# Recording filesystem path
RECPATH = '/var/lib/pisurv'
# Recording ZIP name
RECZIP = 'PiSurv.zip'

# Flask app object for this module
app = Flask(__name__)

@app.route('/')
def recording_list():
    """Handler for recording list (root)"""
    recordings = sorted([rec for rec in os.listdir(RECPATH)
                          if rec.endswith('.mp4')])
    return render_template('index.html', recordings=recordings)

@app.route('/delete', methods=['POST'])
def delete_files():
    """Handler for deleting selected recordings"""
    for rec in request.form.getlist('files'):
      os.remove(os.path.join(RECPATH, rec))
    return redirect(url_for('recording_list'))

@app.route('/download', methods=['POST'])
def download_files():
    """Handler for creating and downloading a ZIP of selected recordings"""
    with zipfile.ZipFile(os.path.join(RECPATH, RECZIP), 'w') as rec_zip:
      for rec in request.form.getlist('files'):
        rec_zip.write(os.path.join(RECPATH, rec), rec)
    return redirect('/rec/' + RECZIP)

def start_server():
    """Start the server"""
    app.run(host='0.0.0.0', port=5005)

# Run the server if this is the main module
if __name__ == '__main__':
    start_server()

