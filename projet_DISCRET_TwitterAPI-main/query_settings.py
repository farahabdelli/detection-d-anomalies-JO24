
class QueryParams():
  REQUEST_TYPE = 'standard'
  keywords = {
      'capitol' :
      '%23attack OR attack OR %23police OR police OR %23violence OR violence '\
        'OR damage OR injury OR %23explosion OR explosion OR %23assault OR assault '\
        'OR %23shooting OR shooting OR security OR %23Trump OR Trump OR %23JoeBiden OR JoeBiden '\
        'OR %23jan6 OR %23elections OR elections '\
        'OR %23maga OR %23makeamericagreatagain OR %23stopthesteal OR %23presidenttrump4moreyears '\
        'OR %23saveamericamarch OR %23saveamerica OR %23Capitol OR Capitol OR %23CapitolRiots ',
          

    'mots_fonctionnels' : '%23attaque OR %23attentat OR %23decapitation OR %23terroriste '\
              'OR %23couteau OR attaque OR attentat OR décapitation OR '\
              'terroriste OR couteau',
    'covid': 'covid',
    }
  
  #tweet_mode : valeurs possibles 'extended' ou ''. Marche uniquement pour l'historique standard
  paramsStandard = {
    'since': '2021-02-05',
    'until': '2021-02-10',
    'count': '100',
    'tweet_mode': 'extended',
    'max_id': '',
    'keywords': keywords['covid']
    }
  paramsPremium = {
    'maxResults': '100',
    'fromDate': '202101250100',
    'toDate': '202101302350',
    'keywords': keywords['covid']
    }


class emailParams:
    sender_email = ''
    password = ''
    #Liste des destinataires pour les alertes mail. 1 destinataire minimum, pas de maximum
    receiver_emails = ['']
    subject= 'Informations collecte en cours'
    #Un message informant le bon déroulement de la collecte est envoyé toutes les 2 heures
    notification_delay_sec = 7200
    

class FileParams():
  wd = './'
  data_folder = 'data_historique'
  tweets_limit_per_file = 100000