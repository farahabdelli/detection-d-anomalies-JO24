
import json
from datetime import datetime

twitter_time_format = "%a %b %d %H:%M:%S +0000 %Y"

class TwitterResponse():
  """Methods to process a request response from Twitter.
  """
  def __init__(self, response):
    """Initialized using a request response object."""
    self.response = response
    self.json = json.loads(response.text)

  @property
  def tweets(self):
    """Returns a list of tweets if the response contains a 'statuses' field"""
    if 'statuses' in self.json:
      return self.json['statuses']
    return None

  @property
  def status_code(self):
    """Returns the int status_code of the Twitter response"""
    return self.response.status_code

  def no_more_tweets(self):
    """Returns a boolean indicating if the request did not match any tweets.
    The function checks if the response contains a tweets list and if its length
    is positive.
    """
    return self.tweets!=None and len(self.tweets)==0

  def get_next_query(self):
    """Returns an str query using the next_results field of a response.
    """
    if 'search_metadata' in self.json:
      return self.json['search_metadata']['next_results']
    return None

  def get_next(self):
     return '&next={}'.format(self.json['next'])

  def get_since_id(self):
    """Returns the max tweet id in a response."""
    return str(self.extract_max(by='id'))

  def extract_max(self, by='id'):
    """Returns the max tweet id (int) or time in a response.
    Args:
      by: str, determines what field of the tweet to compare.
          accepted values are 'id' or 'created_at'
    """
    if self.tweets==None or len(self.tweets)==0:
      return None
    if by=='id':
      return max([tweet['id'] for tweet in self.tweets])
    elif by=='created_at':
      return max([Tweet(t).extract_date() for t in self.tweets])

  def extract_min(self, by='id'):
    """Returns the min tweet id (int) or time in a response.
    Args:
      by: str, determines what field of the tweet to compare.
          accepted values are 'id' or 'created_at'
    """
    if self.tweets==None or len(self.tweets)==0:
      return None
    if by=='id':
      return min([tweet['id'] for tweet in self.tweets])
    elif by=='created_at':
      return min([Tweet(t).extract_date() for t in self.tweets])

class Tweet():
  """class to manage a tweet (status object in a Twitter response)."""
  def __init__(self, tweet):
    self.json = tweet

  def extract_date(self):
    """Returns the date at which the tweet was created."""
    return datetime.strptime(self.json['created_at'], twitter_time_format)
