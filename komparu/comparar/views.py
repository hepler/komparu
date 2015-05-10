# Django
from django.http import HttpResponse
from django.shortcuts import render

# other
import urllib2
import urllib
import unirest
import json as simplejson
import cStringIO


def index(request):
    """ Return index page. """
    title = '...'
    item_left = 'doge'
    item_right = 'dolphin'
    stats = [None]

    # if user entered items, use them
    if request.method == "POST":
        title = 'RESULTS...'
        item_left = request.POST['input_left']
        item_right = request.POST['input_right']
        # stats = aggregateScores(item_left, item_right)

    # now find images for them
    image_left = getImage(item_left)
    image_right = getImage(item_right)

    return render(request, 'index.html', {
        'title': title,
        'item_left': item_left,
        'item_right': item_right,
        'image_left': image_left,
        'image_right': image_right,
        'stats': stats
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
    fetcher = urllib2.build_opener()
    search_result_index = '0'
    search_query = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=' + item + '&start=' + search_result_index
    f = fetcher.open(search_query)
    deserialized_output = simplejson.load(f)

    image_url = deserialized_output['responseData']['results'][0]['unescapedUrl']

    return image_url
