
def query_builder(query_params, REQUEST_TYPE):
    if not 'keywords' in query_params:
        raise ValueError('keywords key not defined.')
    if REQUEST_TYPE == 'standard':
        query = ['?q={}'.format(query_params['keywords'])]
    elif REQUEST_TYPE == 'fullarchive' or REQUEST_TYPE == '30days':
        query = ['?query={}'.format(query_params['keywords'])]
    for k,v  in query_params.items():
        if k != 'keywords':
            query.append('&' + k + '=' + str(v))
    return ''.join(query)
        
