import sys
import re
import os
import imp
import twitter

from django.core.management import setup_environ

from django.conf import settings
from reappy import SearchApplication
from twitter_collector.models import Tweet, User, Tag

twitter_api = twitter.Api()

def all_tweets(tweet):
    try:
        user = User.objects.get(screen_name=tweet.user.user_name)
    except User.DoesNotExist:
        u = twitter_api.GetUser(tweet.user.user_name)
        user = User(screen_name=u.screen_name,
                    user_id=u.id,
                    name=u.name,
                    description=u.description,
                    url=u.url,
                    statuses_count=u.statuses_count,
                    followers_count=u.followers_count,
                    friends_count=u.friends_count,
                    favorites_count=u.favourites_count)
        user.save()

    text = tweet.clean_text
    text = text.strip()
    t = Tweet(raw_text=tweet.raw_text,
              created=tweet.created,                  
              clean_text=text,
              tweet_id=tweet.id,
              user=user)
    t.save()
    for htag in tweet.hashtags:
        try:
            tag = Tag.objects.get(name=htag)
        except Tag.DoesNotExist:
            tag = Tag(name=htag)
            tag.save()
        t.tags.add(tag)
    t.save()
    print "Inserted", text, t.tweet_id

app = SearchApplication(settings.TWITTER_SEARCH_TERM, 
                        [ (r".*", all_tweets)]
                        )
if 'loop' in sys.argv:
    app.loop()
else:
    app.run()
