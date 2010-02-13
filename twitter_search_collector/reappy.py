from urllib2 import urlopen, Request
from urllib import urlencode
from dateutil import parser
import os
import re
import cPickle
import time
try:
    import simplejson as json
except ImportError:
    import json

USER_AGENT = "reappy application/0.1"
hashtag_regex = re.compile(r"(?:[^&]|^)#([a-z0-9_\-]+)")

from twitter_collector.models import _LastRetrieved

class User:
    def __init__(self, data):
        self.profile_image_url = data['profile_image_url']
        self.user_name = data['from_user']

class Tweet:
    def __init__(self, data):
        self.user = User(data)
        self.raw_text = data['text']
        self.id = data['id']
        self.source = data['source']
        self.language = data.get('iso_language_code', 'en')
        self.created = parser.parse(data['created_at'])
        self.hashtags = hashtag_regex.findall(data['text'])
        self.clean_text = hashtag_regex.sub("", self.raw_text)
    
class Application():
    def __init__(self, handlers):
        self.since_id_path = os.path.join(os.path.dirname(__file__), 'since_id.data')
        self.handlers = [(re.compile(r[0], re.IGNORECASE), r[1]) for r in handlers]

    def _persist_since_id(self):
        self.last_retrieved.last_id = self.since_id
        self.last_retrieved.save()

    def run(self):
        tweets = self.get_tweets_since()[::-1]
        for t in tweets:
            for r, h in self.handlers:
                match = r.match(t.raw_text)
                if match:
                    kargs = match.groupdict()
                    h(t, **kargs)
            self.since_id = t.id
            self._persist_since_id()


    def loop(self, poll_frequency=5):
        while True:
            self.run()
            time.sleep(poll_frequency)

class SearchApplication(Application):
    def __init__(self, search_term, handlers):        
        Application.__init__(self, handlers)
        self.search_term = search_term
        try:
            self.last_retrieved = _LastRetrieved.objects.get(search_term=search_term)
            self.since_id = self.last_retrieved.last_id
        except _LastRetrieved.DoesNotExist:
            self.last_retrieved = _LastRetrieved(search_term=search_term)
            self.last_retrieved.save()
            self.since_id = None

        
    def _grab_results(self, search_url):
        req = Request(search_url, headers={'User-Agent': USER_AGENT})
        results = json.loads(urlopen(req).read())
        return results

    def _build_url(self, search_query, since_id=None):
        params = {'q':search_query, 'rpp':100}
        if since_id: params['since_id'] = since_id
        return "http://search.twitter.com/search.json?" + urlencode(params)

    def get_tweets_since(self):        
        url = self._build_url(self.search_term, since_id=self.since_id)
        print url
        return [Tweet(rd) for rd in self._grab_results(url)['results']]
