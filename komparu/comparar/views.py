# Django
from django.shortcuts import render

# Other
import urllib2
import urllib
import json

# APIs
from angelList import AngelListAPI
from genderGuesser import GenderGuesserAPI
from googleBooks import GoogleBooksAPI
from googleResults import GoogleResultsAPI
from thesaurus import ThesaurusAPI
from tweetSentiment import TweetSentimentAPI
from calculator import Calculator


def index(request):
    """ Return index page. """
    title = '...'
    item_left = 'doge'
    item_right = 'dolphin'
    stats = None
    amazon_url = None
    winner = None
    loser = None

    # if user entered items, use them
    if request.method == "POST":
        title = ' RESULTS...'
        item_left = request.POST['input_left']
        item_right = request.POST['input_right']
        stats = CALCULATOR.get_scores(item_left, item_right)

    # get the Amazon URL for whichever item is better, tell the view who is the queen/king
    if stats:
        if stats[item_left] >= stats[item_right]:
            winner = item_left
            loser = item_right
            amazon_url = getAmazonURL(item_left)
        else:
            winner = item_right
            loser = item_left
            amazon_url = getAmazonURL(item_right)


    # now find images for them
    image_left = getImage(item_left)
    image_right = getImage(item_right)

    return render(request, 'index.html', {
        'title': title,
        'item_left': item_left,
        'item_right': item_right,
        'image_left': image_left,
        'image_right': image_right,
        'amazon_url': amazon_url,
        'stats': stats,
        'winner': winner,
        'loser': loser
    })


def getImage(item):
    """ Returns link to an image of the desired item.

    Parameters
    ----------
    item: string
        the search term that the user entered
    """

    # replace whitepace for use in URL
    item = item.replace(' ', '%20')

    # query on the item, grab the url for the first image result
    query_builder = urllib2.build_opener()
    search_result_index = '0'
    search_query = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=' + item + '&start=' + search_result_index
    query_results = query_builder.open(search_query)
    deserialized_output = json.load(query_results)

    image_url = deserialized_output['responseData']['results'][0]['unescapedUrl']

    return image_url


def getAmazonURL(item):
    """
    A utility for retrieving the Amazon search results URL for some item.
    """

    return "http://www.amazon.com/s?field-keywords={0}".format(urllib.quote_plus(item))


angelListAPI = AngelListAPI()
genderGuesserAPI = GenderGuesserAPI()
googleBooksAPI = GoogleBooksAPI()
googleResultsAPI = GoogleResultsAPI()
thesaurusAPI = ThesaurusAPI()
tweetSentimentAPI = TweetSentimentAPI()

APIS = [angelListAPI, genderGuesserAPI, googleBooksAPI, googleResultsAPI, thesaurusAPI, tweetSentimentAPI]
CALCULATOR = Calculator(APIS)
