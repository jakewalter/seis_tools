#!/usr/bin/env python
"""Python method to send updates to twitter."""
import sys
import tweepy

consumer_key='ZvAryzCQfwB3EPXVW34FwQ'
consumer_secret='gtYVoaax3xI4rNBPaQSvKPNwynGy6MnHuVFYIdZo'
access_key='2374878014-9JwoJ9KoP8WX0c6sGzgkYMyCIMf32Sl4qFdmFMi'
access_secret='uUYOi6ki8ZCeI04HJpnRF4kgyDQRtGWOSBZrtjG0W3kJl'

if not access_key:
  auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth_url = auth.get_authorization_url()
  print 'Please authorize: ' + auth_url
  verifier = raw_input('PIN: ').strip()
  auth.get_access_token(verifier)
  print "ACCESS_KEY = '%s'" % auth.access_token.key
  print "ACCESS_SECRET = '%s'" % auth.access_token.secret
else:
  auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_key, access_secret)
  api=tweepy.API(auth)
  if len(sys.argv)==1:
    msg=raw_input("Status: ")
  else:
    msg=sys.argv[1]
  api.update_status(msg)
