from django.db import models

class User(models.Model):
    user_id = models.CharField(max_length=64)
    screen_name = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=140, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    statuses_count = models.IntegerField()
    followers_count = models.IntegerField()
    friends_count = models.IntegerField()
    favorites_count = models.IntegerField()

class Tweet(models.Model):
    raw_text = models.CharField(max_length=140)
    clean_text = models.CharField(max_length=140)
    tweet_id = models.CharField(max_length=140) #No BigInt field yet
    created = models.DateTimeField()
    user = models.ForeignKey(User, related_name="tweets")
    tags = models.ManyToManyField("Tag", related_name="tweets")

class Tag(models.Model):
    name = models.CharField(max_length=140)

class _LastRetrieved(models.Model):
    search_term = models.CharField(max_length=140)
    last_id = models.CharField(max_length=140, null=True, blank=True)
