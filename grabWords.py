import pickle
import requests
from IPython.display import HTML
import string

subscription_key = "bd99b8f704954d0287dd5adba6bced4f"

#load every word into a list, and store it as a pickle entry
def loadAndStore(file, outputName):
    words = []
    fp = open(file, 'r')
    for x in fp:
        words.append(x)
    pickle.dump(words, open(outputName, 'wb'))

#loadAndStore('nouns.txt', 'nouns')
#loadAndStore('words.txt', 'words')

loadAndStore('actions.txt', 'actions')
loadAndStore('places.txt', 'places')


def scrape_google(searchTerm):
    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params  = {"q": searchTerm, "textDecorations":True, "textFormat":"HTML"}
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    return search_results

printable = set(string.printable)

searchTermResults = pickle.load(open('searchTermResults', 'rb'))
s = searchTermResults["space"]["webPages"]['value']

for element in s:
    for key, value in element.items():
        print(filter(lambda x: x in printable, element['snippet']))

#search_term = "space"
#result = scrape_google(search_term)

#searchTermResults[search_term] = result
#print(result)

#pickle.dump(searchTermResults, open('searchTermResults', 'wb'))
