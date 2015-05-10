from django.http import HttpResponse
from django.shortcuts import render
import urllib2
import urllib
import json as simplejson
import cStringIO


def index(request):
    """ Return index page. """

    # get the two items, find images for them
    item_left = 'doge'
    item_right = 'dolphin'
    image_left = getImage(item_left)
    image_right = getImage(item_right)

    return render(request, 'index.html', {
        'title': 'RESULTS...',
        'item_left': item_left,
        'item_right': item_right,
        'image_left': image_left,
        'image_right': image_right
    })


def getImage(item):
    """ Returns link to an image of the desired item.

    Parameters
    ----------
    item: string
        the search term that the user entered
    """

    fetcher = urllib2.build_opener()
    searchTerm = item
    startIndex = 0
    searchUrl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + searchTerm + "&start=" + str(startIndex)
    f = fetcher.open(searchUrl)
    deserialized_output = simplejson.load(f)

    imageUrl = deserialized_output['responseData']['results'][0]['unescapedUrl']

    return imageUrl
