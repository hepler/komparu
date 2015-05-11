# Django
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Other
import urllib2
import urllib
import json
from random import randint

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
    stats = None
    amazon_url = None
    winner = None
    loser = None

    # if user entered items, immediately redirect to GET call with query parameters
    if request.method == "POST":
        item_left = request.POST['input_left'].title()
        item_right = request.POST['input_right'].title()
        return HttpResponseRedirect("/?left={0}&right={1}".format(item_left, item_right))

    # both query parameters, so proceed
    elif "left" in request.GET and "right" in request.GET:
        title = ' RESULTS...'
        item_left = request.GET.get("left")
        item_right = request.GET.get("right")
        stats = CALCULATOR.get_scores(item_left, item_right)
        print stats

    # left query parameter but not right
    elif "left" in request.GET:
        return render(request, 'index.html', {
            'title': ' :(',
            'status': 'fail',
            'failure_description': '"left" query parameter given but not "right" query parameter'
        })

    # right query parameter but not left
    elif "right" in request.GET:
        print '"right" query parameter given but not "left" query parameter'
        return render(request, 'index.html', {
            'title': ' :(',
            'status': 'fail',
            'failure_description': '"right" query parameter given but not "left" query parameter'
        })

    # get the Amazon URL for whichever item is better, tell the view who is the queen/king
    if stats:
        if stats[item_left] >= stats[item_right]:
            winner = strip_last_s(item_left)
            loser = strip_last_s(item_right)
            amazon_url = getAmazonURL(item_left)
        else:
            winner = strip_last_s(item_right)
            loser = strip_last_s(item_left)
            amazon_url = getAmazonURL(item_right)
        difference = int(stats['difference'] * 100)
        # now find images for them
        image_left = getImage(item_left)
        image_right = getImage(item_right)

        # make sure we are getting real things...
        if (image_left == "no result") or (image_right == "no result"):
            return render(request, 'index.html', {
                'title': ' :(',
                'status': 'fail',
                'failure_description': 'no image associated with user request',
                'item_left': item_left,
                'item_right': item_right,
                'image_left': image_left,
                'image_right': image_right
            })

        return render(request, 'index.html', {
            'title': title,
            'status': 'success',
            'item_left': item_left,
            'item_right': item_right,
            'image_left': image_left,
            'image_right': image_right,
            'amazon_url': amazon_url,
            'stats': stats,
            'winner': winner,
            'loser': loser,
            'difference': difference
        })

    # if there's no POST then return blank index
    return render(request, 'index.html', {
        'title': title,
        'status': None
    })

def strip_last_s(item):
    if item.lower().endswith("s"):
        return item[:-1]
    else:
        return item


def getImage(item):
    """ Returns link to an image of the desired item.

    Parameters
    ----------
    item: string
        the search term that the user entered
    """

    # replace whitepace for use in URL
    item = item.replace(' ', '%20')
    try:
        random_index = randint(0, 10)
        # query on the item, grab the url for the first image result
        query_builder = urllib2.build_opener()

        search_result_index = str(random_index)
        search_query = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=' + item + '&start=' + search_result_index
        query_results = query_builder.open(search_query)
        deserialized_output = json.load(query_results)

        image_url = deserialized_output['responseData']['results'][0]['unescapedUrl']
    except:
        image_url = "no result"

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
