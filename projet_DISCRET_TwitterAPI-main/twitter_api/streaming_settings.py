class authParams:
    Consumer_key = ''
    Consumer_secret = ''
    Access_token = ''
    Access_token_secret = ''



class filterParams:
    '''
    filterParams: 
    Paramètres de filtres
    languagesFilter : Laisser le tableau vide si aucun filtre de langue n'est souhaité
    locationsFilter : Laisser le tableau vide si aucun filtre de géolocalisation n'est souhaité
    Si filtre géo activé et mots clés cherchés, le match se fera avec tweets ayant mots-clés OU se trouvant dans la zone
    '''
    trackedFreeWords = ['']
    
    trackedHashtags = ['#attack']
    
    #Exemple : languagesFilter = ['fr']
    languagesFilter = ['en']
    locationsFilter = []
    
    
class fileParams:
    #Un nouveau fichier jsonl sera créé dès que ce nombre de tweets sera atteint
    tweets_limit_per_file = 1000000
    data_directory = './'


class emailParams:
    sender_email = ''
    password = ''
    #Liste des destinataires pour les alertes mail. 1 destinataire minimum, pas de maximum
    #Format : receiver_emails = ['adresse1@exemple.fr', 'adresse2@test.fr']
    receiver_emails = []
    subject= 'Informations collecte en cours'
    #Un message informant le bon déroulement de la collecte est envoyé toutes les 2 heures
    notification_delay_sec = 7200