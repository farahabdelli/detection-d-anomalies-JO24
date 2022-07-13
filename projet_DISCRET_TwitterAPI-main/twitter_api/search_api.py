

import time
import requests
from twitter_api import collection_logging
from twitter_api.TwitterResponse import TwitterResponse
import urllib3
from requests.exceptions import ConnectionError
from query_settings import emailParams, QueryParams
import sys
from datetime import datetime
from twitter_api import notifications
from threading import Timer

twitter_time_format = "%a %b %d %H:%M:%S +0000 %Y"
in_error = False
temps_attente = 2*60

def send_alive_email():
    global in_error
    if in_error == False:
        notifications.send_alive_email()
    Timer(emailParams.notification_delay_sec, send_alive_email).start()

def handle_error(exception, error_type):
    base_error_message = 'La collecte s\'est arrêtée. \nErreur ({}) : {}\n'\
              'Date de l\'erreur :{}\n.'
    global in_error
    collection_logging.error_log(exception)
    if in_error == False:
        messageContent = base_error_message.format(error_type, exception, datetime.now())
        notifications.send_error_email(messageContent)
        in_error = True

class StandardSearch():
  """Methods to interact with the standard search api
  """
  search_url = 'https://api.twitter.com/1.1/search/tweets.json'
  pause_sec = 5
  pause_429_sec = 3*60

  @staticmethod
  def historical_search(oauth, query):
    """Retreives tweets corresponsing to a search query from the standard api.
    Args:
      oauth: oauth request
      query: an str of the query
    Returns:
      An iterable of response objects
    """
    global in_error
    count_tweets = 0
    
    send_alive_email()
    while True:
      try:
        response = StandardSearch.get_response(oauth, query)
        yield response

        count_tweets = collection_logging.log_total_tweets(
              count_tweets, response)

        twitter_response = TwitterResponse(response)

        if twitter_response.status_code == 200:
          time.sleep(StandardSearch.pause_sec)
          if in_error == True:
            in_error = False
            notifications.send_reprise_email()
            collection_logging.reprise_log()
          if twitter_response.no_more_tweets():
            break
          query = twitter_response.get_next_query()
        elif twitter_response.status_code in [503, 429]:
          time.sleep(StandardSearch.pause_429_sec)
          continue
      except (urllib3.exceptions.ProtocolError, urllib3.exceptions.ReadTimeoutError, ConnectionError) as exc:
        handle_error(exc, 'connue')
        time.sleep(temps_attente)
      except KeyboardInterrupt:
        handle_error('Interruption manuelle', 'connue')
        sys.exit(0)

  @staticmethod
  def get_response(oauth, query):
    """Returns a request response and logs query and response details.
    Args:
      oauth: oauth request
      query: an str of the query
    """
    collection_logging.pre_request_log(query)
    response = oauth.get(StandardSearch.search_url + query)
    collection_logging.post_request_log(TwitterResponse(response))
    return response


class PremiumSearch():
    
    def __init__(self, request_type, bearer_token):
        if request_type == 'fullarchive':
            self.search_url = 'https://api.twitter.com/1.1/tweets/search/fullarchive/Dev2.json'
        elif request_type == '30days':
            self.search_url = 'https://api.twitter.com/1.1/tweets/search/30day/dataengineercollect1.json'
        self.bearer_token = bearer_token
    
    pause_429_sec = 3*60
    pause_sec = 1.01
    nextPageParam = ''
    
    @staticmethod
    def historical_search(self, oauth, query):
        global in_error
        send_alive_email()
        count_tweets = 0
        base_query = query
        while True:
          try:
              response = PremiumSearch.get_response(self, oauth, query)
              yield response
        
              count_tweets = collection_logging.log_total_tweets(
                    count_tweets, response)
        
              twitter_response = TwitterResponse(response)
        
              if twitter_response.status_code == 200:
                time.sleep(PremiumSearch.pause_sec)
                if in_error == True:
                    in_error = False
                    notifications.send_reprise_email()
                    collection_logging.reprise_log()
                if twitter_response.no_more_tweets():
                  break
                query = base_query + twitter_response.get_next()
              elif twitter_response.status_code in [503, 429]:
                time.sleep(PremiumSearch.pause_429_sec)
                continue
          except (urllib3.exceptions.ProtocolError, urllib3.exceptions.ReadTimeoutError, ConnectionError) as exc:
              handle_error(exc, 'connue')
              time.sleep(temps_attente)
          except KeyboardInterrupt:
              handle_error('Interruption manuelle', 'connue')
              sys.exit(0)

    
    def get_response(self, oauth, query):
        collection_logging.pre_request_log(query)
        response = oauth.get(self.search_url + str(query) + PremiumSearch.nextPageParam, auth=BearerAuth(self.bearer_token))
        collection_logging.post_request_log(TwitterResponse(response))
        return response



class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r
        
