
import json
import os
import pathlib
import time


def write_tweets(filename, response, request_type):
  """
  Writes tweets to a file.
  Args:
    filename: str, file to which the tweets are written
    response: A request response object.
    request_type : can be standard, 30days or fullarchive. Defined in query_settings.py
  """
  jsonResponse = json.loads(response.text)
  if request_type == 'standard':
    if not 'statuses' in jsonResponse:
      return
    tweets = jsonResponse['statuses']
  elif request_type == 'fullarchive' or request_type == '30days':
    tweets = jsonResponse['results']

  with open(filename, 'a+', encoding="utf-8") as f:
    for tweet in tweets:
      json.dump(tweet, f)
      f.write('\n')


def create_directory(directory):
  """Creates a directory."""
  pathlib.Path(directory).mkdir(parents=True, exist_ok=True)


def set_directory(FileParams, FileName):
  """Creates output folder and files and returns the log_file and data_file."""
  data_directory = os.path.join(FileParams.wd, FileParams.data_folder)
  create_directory(data_directory)

  execution_time = time.strftime("%Y%m%d-%H%M%S")
  current_directory = os.path.join(data_directory, execution_time)
  create_directory(current_directory)

  log_file = os.path.join(current_directory, 'log.txt')
  
  return log_file, current_directory


def set_data_file(current_directory, file_number):
    return os.path.join(current_directory, 'tweets_{}.jsonl'.format(file_number))
