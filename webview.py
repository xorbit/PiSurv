#!/usr/bin/env python
"""Raspberry Pi surveillance - web viewer module
Copyright (c) 2014 Patrick Van Oosterwijck
Distributed under GPL v2 license"""

from flask import *
import os
import os.path
import zipfile
from math import ceil
import cfg


# Flask app object for this module
app = Flask(__name__)


# Helper classes and functions

class Pagination(object):
    """Simple pagination class"""

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def in_page(self, idx):
        return idx >= ((self.page-1) * self.per_page) and \
                idx < (self.page * self.per_page)

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

def url_for_other_page(page):
    """Generate a URL for a different page"""
    args = dict(request.view_args.items() + request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


# Route definitions

@app.route('/', defaults={'page': 1})
@app.route('/<int:page>')
def recording_list(page):
    """Handler for recording list (root)"""
    recordings = sorted([rec for rec in os.listdir(cfg.REC_PATH)
                          if rec.endswith('.mp4')])
    if not recordings and page != 1:
        abort(404)
    pagination = Pagination(page, cfg.REC_PER_PAGE, len(recordings))
    return render_template('index.html', recordings=recordings,
                          pagination=pagination)

@app.route('/delete', methods=['POST'])
def delete_files():
    """Handler for deleting selected recordings"""
    for rec in request.form.getlist('files'):
        os.remove(os.path.join(cfg.REC_PATH, rec))
    return redirect(url_for('recording_list'))

@app.route('/download', methods=['POST'])
def download_files():
    """Handler for creating and downloading a ZIP of selected recordings"""
    with zipfile.ZipFile(os.path.join(cfg.REC_PATH, cfg.REC_ZIP),
                          'w') as rec_zip:
        for rec in request.form.getlist('files'):
            rec_zip.write(os.path.join(cfg.REC_PATH, rec), rec)
    return redirect('/rec/' + cfg.REC_ZIP)

def start_server():
    """Start the server"""
    app.run(host='0.0.0.0', port=5005)

# Run the server if this is the main module
if __name__ == '__main__':
    start_server()

