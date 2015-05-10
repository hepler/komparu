# Django
from django.http import HttpResponse
from django.shortcuts import render

# other
import math
import urllib2
import urllib
import unirest
import json
import cStringIO
import operator
import threading


def index(request):
    """ Return index page. """
    title = '...'
    item_left = 'doge'
    item_right = 'dolphin'
    stats = [None]

    # if user entered items, use them
    if request.method == "POST":
        title = ' RESULTS...'
        item_left = request.POST['input_left']
        item_right = request.POST['input_right']
        stats = aggregateScores(item_left, item_right)

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
    query_builder = urllib2.build_opener()
    search_result_index = '0'
    search_query = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=' + item + '&start=' + search_result_index
    query_results = query_builder.open(search_query)
    deserialized_output = json.load(query_results)

    image_url = deserialized_output['responseData']['results'][0]['unescapedUrl']

    return image_url


def aggregateScores(item_left, item_right):
        """ Returns list of scores from the API requests.

        Parameters
        ----------
        item_left: string
            the left side search term from the user
        item_right: string
            the right side search term from the user
        """
        angel_list = AngelListAPI().get_scores(item_left, item_right)
        gender_guesser = GenderGuesserAPI().get_scores(item_left, item_right)
        google_books = GoogleBooksAPI().get_scores(item_left, item_right)
        # google_results = GoogleResultsAPI().get_scores(item_left, item_right)
        thesaurus = ThesaurusAPI().get_scores(item_left, item_right)
        tweet_sentiment = TweetSentimentAPI().get_scores(item_left, item_right)

        scores = [
            angel_list,
            gender_guesser,
            google_books,
            # google_results,
            thesaurus,
            tweet_sentiment
        ]

        return scores


# API calls listed here:

class AngelListAPI:
    def get_scores(self, a, b):
        count_a = self.get_score(a)
        count_b = self.get_score(b)

        total = count_a + count_b

        if total == 0:
            return {a: 0.0, b: 0.0}, "Angel List"

        adjusted_ratio_a = count_a * 1.0 / total / 10
        adjusted_ratio_b = count_b * 1.0 / total / 10

        # more startups means you're probably worse
        return {a: 1.0 - adjusted_ratio_a, b: 1.0 - adjusted_ratio_b}, "Angel List"

    def get_score(self, item):
        response = unirest.get(
            "https://api.angel.co/1/search?query={0}&type=Startup".format(
                urllib.quote_plus(item))
        )

        results = response.body

        if not results:
            return 0
        else:
            return len(results)


class GenderGuesserAPI:
    def get_scores(self, a, b):
        score_a = self.get_score(a)
        score_b = self.get_score(b)
        return {a: score_a, b: score_b}, "Gender Guesser"

    def get_score(self, item):
        response = unirest.get(
            "https://montanaflynn-gender-guesser.p.mashape.com/?name={0}".format(
                urllib.quote_plus(item)),
            headers={
                "X-Mashape-Key": "SuRl5yqxrrmsh4S2wAFlX9vmDWFUp1zg4Nsjsn9pi3WOXUUhwW",
                "Accept": "application/json"
            }
        )

        try:
            gender = response.body["gender"]
        except:
            # no gender response (or any error) means neutral
            return 1.0

        if not gender:
            return 1.0
        elif gender == "female":
            return 1.5
        elif gender == "male":
            return 0.5
        else:
            # non-binary genders get a bonus
            return 2.0


class GoogleBooksAPI:
    def get_scores(self, a, b):
        count_a = self.get_score(a)
        count_b = self.get_score(b)

        score_a = 1.0 + count_a / 10000.0
        score_b = 1.0 + count_b / 10000.0

        # more pages, more better
        return {a: score_a, b: score_b}, "Google Books"

    def get_score(self, item):
        response = unirest.get(
            "https://www.googleapis.com/books/v1/volumes?q={0}&maxResults=40".format(
                urllib.quote_plus(item))
        )

        results = response.body

        if not results:
            return 0
        else:
            return sum(volume["volumeInfo"].get("pageCount", 0.0) for volume in results.get("items"))


class GoogleResultsAPI:
    cats = float(134000000) # number of cats this metric finds

    def get_scores(self, a, b):
        results_a = self.get_results(a)
        results_b = self.get_results(b)

        return {a: GoogleResults.calculate_score(results_a), b: GoogleResults.calculate_score(results_b)}, "Google Search"

    @staticmethod
    def calculate_score(results):
        return (results - GoogleResults.cats) / GoogleResults.cats + 1

    @staticmethod
    def get_results(item):
        url = 'https://www.googleapis.com/customsearch/v1?num=1&key=AIzaSyANy3-2kx-9_Mx8IlnuefRF-gQ17jZoMgE&cx=006715939817891416696:lc2hb0t40r0&q={}'
        response = unirest.get(
            url.format(urllib.quote_plus(item)),
            headers={
                "Accept": "application/json"
            }
        )

        return int(response.body["searchInformation"]["totalResults"])


class ThesaurusAPI:
    def get_scores(self, a, b):
        count_a = self.get_score(a)
        count_b = self.get_score(b)

        total = count_a + count_b

        if total == 0:
            return {a: 0.0, b: 0.0}, "Thesaurus"

        ratio_a = count_a * 1.0 / total
        ratio_b = count_b * 1.0 / total

        return {a: 1.0 + ratio_a, b: 1.0 + ratio_b}, "Thesaurus"

    def get_score(self, item):
        response = unirest.get(
            "http://words.bighugelabs.com/api/2/1992b053499e0716fe1b8308c5c40727/{0}/json".format(
                urllib.quote_plus(item)))

        if response.body:
            synonym_lists = self.get_all_lists(response.body, "syn")
            synonyms = sum(len(l) for l in synonym_lists)
            antonym_lists = self.get_all_lists(response.body, "ant")
            antonyms = sum(len(l) for l in antonym_lists)
        else:
            synonyms = 0
            antonyms = 0

        # the more haters you have, the more points you get
        return 2 * antonyms + synonyms

    def get_all_lists(self, body, key):
        lists = []
        for tense in body:
            if body[tense].get(key):
                lists.append(body[tense].get(key))
        return lists


class TweetSentimentAPI:
    def get_scores(self, a, b):
        score_a = self.get_score(a)
        score_b = self.get_score(b)
        return {a: score_a, b: score_b}, "Twitter Sentiment"

    def get_score(self, item):
        response = unirest.get(
            "https://jamiembrown-tweet-sentiment-analysis.p.mashape.com/api/?key=28413a7af0696d7b4e2e72b47329d76c812d59db&text={0}".format(
                urllib.quote_plus(item)),
            headers={
                "X-Mashape-Key": "SuRl5yqxrrmsh4S2wAFlX9vmDWFUp1zg4Nsjsn9pi3WOXUUhwW",
                "Accept": "application/json"
            }
        )

        return math.fabs(response.body["score"])
