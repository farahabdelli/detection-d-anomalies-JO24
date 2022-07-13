
from twitter_api import collection_logging
from twitter_api.search_api import StandardSearch
from twitter_api.search_api import PremiumSearch
from twitter_api import output_management
from twitter_api import query_building
from query_settings import FileParams
from query_settings import QueryParams
from requests_oauthlib import OAuth1Session
import oauth_settings

consumer_key = oauth_settings.Consumer_key
consumer_secret = oauth_settings.Consumer_secret
access_token = oauth_settings.Access_token
access_token_secret = oauth_settings.Access_token_secret
bearer_token = oauth_settings.Bearer_token
REQUEST_TYPE = QueryParams.REQUEST_TYPE

def get_page_size():
    if REQUEST_TYPE == 'standard':
        if 'count' in QueryParams.paramsStandard:
            return QueryParams.paramsStandard['count']
        else:
            return 100
    elif REQUEST_TYPE == '30days' or REQUEST_TYPE == 'fullarchive':
        if 'maxResults' in QueryParams.paramsPremium:
            return QueryParams.paramsPremium['maxResults']
        else:
            return 500
    else:
        collection_logging.error_log('Le type de requête spécifié ({}) dans le fichier paramètres est incorrect'.format(REQUEST_TYPE))
        return None

page_size = int(get_page_size())       
        


def main():
  file_number = 0
  compteur_tweet = 0
  tweets_limit_per_file = FileParams.tweets_limit_per_file
  # set up the data directory and the log file
  log_file, current_directory = output_management.set_directory(FileParams, file_number)
  data_file = output_management.set_data_file(current_directory, file_number)
  collection_logging.set_logger(log_file)

  # get the oauth handle
  oauth = OAuth1Session(consumer_key,
                        client_secret=consumer_secret,
                        resource_owner_key=access_token,
                        resource_owner_secret=access_token_secret)


  # historical search
  if REQUEST_TYPE == 'standard':
    query_params = QueryParams.paramsStandard
    query = query_building.query_builder(query_params, REQUEST_TYPE)
    for response in StandardSearch.historical_search(oauth, query):
        compteur_tweet += page_size
        output_management.write_tweets(data_file, response, REQUEST_TYPE) 
        if compteur_tweet >= tweets_limit_per_file:
            file_number += 1
            data_file = output_management.set_data_file(current_directory, file_number)
            compteur_tweet = 0            
  else:
      if REQUEST_TYPE == '30days' or REQUEST_TYPE == 'fullarchive':
          query_params = QueryParams.paramsPremium
          query = query_building.query_builder(query_params, REQUEST_TYPE)
          search = PremiumSearch(REQUEST_TYPE, bearer_token)
          for response in search.historical_search(search, oauth, query):
            compteur_tweet += page_size
            output_management.write_tweets(data_file, response, REQUEST_TYPE) 
            if compteur_tweet >= tweets_limit_per_file:
                file_number += 1
                data_file = output_management.set_data_file(current_directory, file_number)
                compteur_tweet = 0
      else:
          collection_logging.error_log('Le type de requête spécifié ({}) dans le fichier paramètres est incorrect'.format(REQUEST_TYPE))  


if __name__ == "__main__":
  main()
