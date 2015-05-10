# Django
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

bad_result = "https://d13yacurqjgara.cloudfront.net/users/596597/screenshots/1714959/microwave-sad-face_1x.png"

def index(request):
    """ Return index page. """
    title = '...'
    stats = None
    amazon_url = None
    winner = None
    loser = None


    # if user entered items, use them
    if request.method == "POST":
        title = ' RESULTS...'
        item_left = request.POST['input_left'].title()
        item_right = request.POST['input_right'].title()
        stats = CALCULATOR.get_scores(item_left, item_right)
        print stats

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
        difference = int(stats['difference'] * 100)
        # now find images for them
        image_left = getImage(item_left)
        image_right = getImage(item_right)

        # make sure we are getting real things...
        if (image_left == bad_result) or (image_right == bad_result):
            print
            print 'no image associated with user request'
            print
            return render(request, 'index.html', {
                'title': ' :(',
                'status': 'fail',
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
        image_url = "https://d13yacurqjgara.cloudfront.net/users/596597/screenshots/1714959/microwave-sad-face_1x.png"

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
