import tweepy
from streaming_settings import emailParams
from streaming_settings import filterParams
from streaming_settings import fileParams
from streaming_settings import authParams
from notifications import EmailSession
import notifications
import collection_logging
import time
import json
import logging
from datetime import datetime
import os
import pathlib
import sys
from threading import Timer
import urllib3
import http


def create_directory(directory):
  """Creates a directory."""
  pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

execution_time = time.strftime("%Y%m%d-%H%M%S")
collecte_dir = os.path.join(fileParams.data_directory, execution_time)
create_directory(collecte_dir)
log_file = os.path.join(collecte_dir, 'log.txt')
in_error = False
first_connection = True

#Récupération des paramètres de collecte
tracked = filterParams.trackedFreeWords + filterParams.trackedHashtags
languagesFilter = filterParams.languagesFilter
locationsFilter = filterParams.locationsFilter


def writeLog(status, nbTweetsCollected):
    if status == 200:
        logging.info('{}: message received. {} messages collectés.'.format(
            str(datetime.now()), str(nbTweetsCollected)))
    else:
        logging.error('-------- ERROR --------')
        logging.error('Time : ' + str(datetime.now()))
        logging.error('Status code : ' + str(status))
        logging.error('\n')

def log_reprise(nbTweetsCollected):
        logging.info('-------- REPRISE APRÈS ERREUR --------')
        logging.info('Time : ' + str(datetime.now()))
        logging.info('Pool : ' + ', '.join(tracked))
        logging.info('Tweets collectés : ' + str(nbTweetsCollected))
        logging.info('\n')


def setup_oauth():
    #récupération clés d'accès
    Consumer_key = authParams.Consumer_key
    Consumer_secret = authParams.Consumer_secret
    Access_token = authParams.Access_token
    Access_token_secret = authParams.Access_token_secret

    #Authentification via Tweepy
    auth = tweepy.OAuthHandler(Consumer_key, Consumer_secret)
    auth.set_access_token(Access_token, Access_token_secret)
    return auth


def setup_logging():
    root_logger= logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file, 'w', 'utf-8')
    root_logger.addHandler(handler)


class ErrorHandling():
    base_error_message = 'La collecte s\'est arrêtée. \nErreur ({}) : {}\n'\
              'Date de l\'erreur :{}\n.Mots/hashtags trackés : {}.'
    @staticmethod
    def handle_error(exception, error_type):
        global in_error

        logging.info('Time : ' + str(datetime.now()))
        logging.info('Erreur : ' + str(exception))
        logging.info('\n')
        messageContent = ErrorHandling.base_error_message.format(
                  error_type, exception, datetime.now(), ', '.join(tracked))
        if in_error == False:
          email_session = EmailSession(emailParams, 1)
          email_session.sendMail(messageContent)
          email_session.close()
          in_error = True
          
    @staticmethod
    def handle_known_error(exception, stopTime=0):
        ErrorHandling.handle_error(exception, 'connue')
        time.sleep(stopTime)

    @staticmethod
    def handle_unknown_error(exception):
        ErrorHandling.handle_error(exception, 'inconnue')
        time.sleep(60)


class StreamListener(tweepy.StreamListener):
    nbTweetsCollected = 0
    nbFile = 1
    tweetFileCounter = 0
    tweets_per_file_counter = 0
    tweets_limit_per_file = fileParams.tweets_limit_per_file
    tweets_file = os.path.join(collecte_dir, 'tweets_{}.jsonl'.format(nbFile))

    execution_time = time.strftime("%Y%m%d-%H%M%S")
    def on_data(self, raw_data):
        self.process_data(raw_data)
        return True

    def process_data(self, raw_data):
        global in_error
        self.tweets_per_file_counter += 1

        #Si on arrive au seuil de tweets, la collecte continue dans un nouveau
        #fichier jsonl. Le chemin d'accès tweet_file est mis à jour.
        if self.tweets_per_file_counter > self.tweets_limit_per_file:
            self.nbFile += 1
            self.tweets_per_file_counter = 0
            self.tweets_file = os.path.join(collecte_dir, 'tweets_{}.jsonl'.format(self.nbFile))

        data_json = json.loads(raw_data)
        if in_error == True:
            in_error = False
            messageContent = 'Reprise de la collecte à {}.'.format(
                datetime.now())
            email_session = EmailSession(emailParams, 2)
            email_session.sendMail(messageContent)
            email_session.close()
            log_reprise(self.nbTweetsCollected)

        with open(self.tweets_file, 'a+', encoding='utf-8') as f:
            json.dump(data_json, f)
            f.write('\n')
            self.nbTweetsCollected += 1

        #Tous les 100 tweets on écrit dans le log
        writeLog(200, self.nbTweetsCollected)

    def on_status(self, status):
        print(status.text)

    def on_connect(self):
        global first_connection
        #Démarrage de l'envoi régulier de mails informant le bon déroulement de la collecte
        if first_connection:
            send_alive_email()
            first_connection = False

    def on_error(self, status_code):
        writeLog(status_code, self.nbTweetsCollected)


def send_alive_email():
    global in_error
    if in_error == False:
        notifications.send_alive_email()
    Timer(emailParams.notification_delay_sec, send_alive_email).start()


class Stream():
    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self, tracked, languagesFilter, locationsFilter):   
        if not languagesFilter:
            languagesFilter = None
        if not locationsFilter:
            locationsFilter = None
        self.stream.filter(languages=languagesFilter, locations=locationsFilter, track=tracked, stall_warnings=True)
    

def main():
    #Authentification
    api = tweepy.API(setup_oauth(), wait_on_rate_limit = True)

    #Mise en place du logging
    setup_logging()

    listener = StreamListener()
    logging.info('Pool : ' + ', '.join(tracked))
    
    #Démarrage du Stream
    stream = Stream(auth=api.auth, listener=listener)
    
    while True:
        try:
            stream.start(tracked, languagesFilter, locationsFilter)
        except ConnectionError as ce:
            ErrorHandling.handle_known_error(ce)
        except OSError as ose:
            ErrorHandling.handle_known_error(ose)
        except urllib3.exceptions.ProtocolError as pe:
            ErrorHandling.handle_known_error(pe)
        except urllib3.exceptions.ReadTimeoutError as rte:
            ErrorHandling.handle_known_error(rte, 120)
        except http.client.IncompleteRead as ir:
            ErrorHandling.handle_known_error(ir)
        except tweepy.error.TweepError as te:
            ErrorHandling.handle_known_error(te)
        except Exception as e:
            ErrorHandling.handle_unknown_error(e)
        except KeyboardInterrupt:
            ErrorHandling.handle_known_error('Interruption manuelle')
            sys.exit(0)


if __name__ == "__main__":
    main()
