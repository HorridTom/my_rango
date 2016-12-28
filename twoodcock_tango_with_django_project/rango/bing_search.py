import json

import urllib.parse
import urllib.request
import urllib.error
import http.client


# Add your Microsoft Account Key to a file called bing.key


def read_bing_key():
    """
    Reads the BING API key from a file called 'bing.key'.
    Returns: a string which is either the key, or None, i.e. no key found.
    Remember: put bing.key in your .gitignore file to avoid committing it!
    """
    # See Python Anti-Patterns - it's an awesome resource!
    # Here we are using "with" when opening documents.
    # http://docs.quantifiedcode.com/python-anti-patterns/maintainability/
    bing_api_key = None

    try:
        with open('bing.key', 'r') as f:
            bing_api_key = f.readline()
    except:
        raise IOError('bing.key file not found')

    return bing_api_key


def run_query_twd(search_terms):
    """
    Given a string containing search terms (query),
    returns a list of results from the Bing search engine.
    """
    bing_api_key = read_bing_key()

    if not bing_api_key:
        raise KeyError("Bing Key Not Found")

    # Specify the base url and the service (Bing Search API 2.0)
    root_url = 'https://api.cognitive.microsoft.com/bing/v5.0/search'
    service = 'Web'

    # Specify how many results we wish to be returned per page.
    # Offset specifies where in the results list to start from.
    # With results_per_page = 10 and offset = 11, this would start from page 2.
    results_per_page = 10
    offset = 0

    # Wrap quotes around our query terms as required by the Bing API.
    # The query we will then use is stored within variable query.
    query = "'{0}'".format(search_terms)

    # Turn the query into an HTML encoded string, using urllib. Py3.
    query = urllib.parse.quote(query)

    # Construct the latter part of our request's URL.
    # Sets the format of the response to JSON and sets other properties.
#     search_url = "{0}?count={1}&q={2}&safesearch=Moderate&
#     mkt=en-us&offset={3}".format(
#                     root_url,
#                     results_per_page,
#                     query,
#                     offset)
#     print(search_url)
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
                    root_url,
                    service,
                    results_per_page,
                    offset,
                    query)

    # Setup authentication with the Bing servers.
    # The username MUST be a blank string, and put in your API key!
    username = ''

    # Setup a password manager to help authenticate our request.
    # Watch out for the difference between Python 2 and 3! Py3
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

    # The below line will work for both Python versions.
    password_mgr.add_password(None, search_url, username, bing_api_key)

    # Create our results list which we'll populate.
    results = []

    try:
        # Prepare for connecting to Bing's servers.
        # Python 3 import (three lines)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)
        print('Connection preparation complete.')
        print(search_url)

        # Connect to the server and read the response generated.
        response = urllib.request.urlopen(search_url).read()
        response = response.decode('utf-8')
        print('Response generated.')

        # Convert the string response to a Python dictionary object.
        json_response = json.loads(response)

        # Loop through each page returned, populating our results list.
        for result in json_response['d']['results']:
            results.append({'title': result['Title'],
                            'link': result['Url'],
                            'summary': result['Description']})
    except:
        print("Error when querying the Bing API")

    # Return the list of results to the calling function.
    return results


def run_query(search_terms):

    bing_api_key = read_bing_key()

    if not bing_api_key:
        raise KeyError("Bing Key Not Found")

    headers = {
               # Request headers
               'Ocp-Apim-Subscription-Key': bing_api_key,
    }

    params = urllib.parse.urlencode({
                                     # Request parameters
                                     'q': search_terms,
                                     'count': '10',
                                     'offset': '0',
                                     'mkt': 'en-us',
                                     'safesearch': 'Moderate',
                                     })
    print(params)
    print("/bing/v5.0/search?%s" % params)

    # Create our results list which we'll populate.
    results = []

    try:
        conn = http.client.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v5.0/search?%s" % params, "{body}", headers)
        response = conn.getresponse()

        data = response.read()
        data = data.decode('utf-8')

        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    # Convert the string response to a Python dictionary object.
    json_response = json.loads(data)

    # Loop through each page returned, populating our results list.
    for result in json_response['webPages']['value']:
        results.append({'title': result['name'],
                        'link': result['displayUrl'],
                        'summary': result['snippet'],
                        'bingurl': result['url']})

    return results


def main():
    search_results = run_query('cheese')
    for value in search_results:
        print (value['title'], ": ", value['link'])

if __name__ == '__main__':
    main()
