import os
import requests
from datetime import datetime
from flask import Flask, request, session, render_template, make_response, \
                  redirect, url_for

app = Flask(__name__)
app.debug = True
app.secret_key = 'Artoo says that the chances of survival are 725 to 1'
app.config.api = 'http://discussion.guardianapis.com/discussion-api/discussion/'
app.config.timeout = 3


@app.route('/')
def dashboard():
    watching = ['/p/3b556', '/p/3b3xf']
    discussions = []
    for discussion_id in watching:
        discussion = discussion_cache.get(discussion_id)
        if not discussion:
            try:
                discussion = Discussion(discussion_id)
            except requests.exceptions.Timeout:
                pass # Serve stale if we have data
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == requests.codes.not_found:
                    # Doesn't exist, stop watching it
                    watching = [d for d in watching if d != discussion_id]
        discussions.append(discussion)
    return render_template('dashboard.html', discussions=discussions)


@app.route('/subscribe')
def subscribe():
    return redirect(url_for('dashboard'))


class Discussion(object):

    def __init__(self, discussion_id):
        if not hasattr(self, 'key'):
            self.key = discussion_id
            self.api_url = app.config.api + self.key
        self.update()
        self.cache()

    def update(self):
        r = requests.get(self.api_url,
            timeout=app.config.timeout)
        if r.status_code == requests.codes.ok:
            self.parse(r.json.get('discussion'))
        else:
            r.raise_for_status()

    def parse(self, discussion):
        # self.title    = discussion.get('title')
        self.short_url = 'http://gu.com' + self.key
        self.web_url   = discussion.get('webUrl')
        self.comments  = discussion.get('commentCount')
        self.closed    = discussion.get('isClosedForComments')

        if not hasattr(self, 'meta'):
            self.meta = {}
        self.meta['last_updated'] = datetime.now()

    def cache(self):
        discussion_cache.set(self.key, self)


class DiscussionCache(object):

    def __init__(self):
        self.items = {}

    def get(self, key):
        return self.items.get(key)

    def set(self, key, value):
        self.items[key] = value

discussion_cache = DiscussionCache()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
