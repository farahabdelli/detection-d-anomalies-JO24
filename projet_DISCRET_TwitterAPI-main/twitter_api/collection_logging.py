
from datetime import datetime
import logging
from twitter_api.TwitterResponse import TwitterResponse

def error_log(exception):
    logging.info('{}: Erreur : {}.\n'.format(str(datetime.now()), str(exception)))
    
def reprise_log():
    logging.info('{}: Reprise après erreur.\n'.format(str(datetime.now())))

def update_total_tweets(count_tweets, twitter_response):
  """Adds the number of tweets in a response to the total collected number."""
  if twitter_response.tweets is None:
    return count_tweets
  return count_tweets + len(twitter_response.tweets)


def log_total_tweets(count_tweets, response):
  """Updates, logs and returns the total number of tweets collected."""
  count_tweets = update_total_tweets(count_tweets, TwitterResponse(response))
  logging.info('Total number of tweets : {}'.format(count_tweets))
  return count_tweets


def pre_request_log(query):
  """Logs the time and the query (str)."""
  logging.info('Time : {}'.format(str(datetime.now())))
  logging.info('Query : {}'.format(query))


def post_request_log(twitter_response):
  """logs information extracted from a Twitter response.
     logs:
       * the status code of the response
       * If the response contains a 'statuses' field, also logs:
         - Number of collected tweets.
         - La date et temps du tweet le plus ancien dans les tweets obtenus.
         - La date et temps du tweet le plus nouveau dans les tweets obtenus.
      Args:
        twitter_response: A TwitterResponse object.
  """
  logging.info('Status : ' + str(twitter_response.status_code))

  if twitter_response.tweets!=None:
    logging.info('Tweets Collected : {}'.format(
        str(len(twitter_response.tweets))))
    logging.info('First timestamp : {}'.format(
        twitter_response.extract_min('created_at')))
    logging.info('Last timestamp :  {}'.format(
        twitter_response.extract_max('created_at')))
  logging.info('\n')


def set_logger(log_file):
  """
  Sets the logging parameters and output file.
  Args:
    log_file: filename (str) where the log is saved.
  """
  root_logger= logging.getLogger()
  root_logger.setLevel(logging.INFO)
  handler = logging.FileHandler(log_file, 'w', 'utf-8')
  #handler.setFormatter(logging.Formatter('%(name)s %(message)s'))
  root_logger.addHandler(handler)
