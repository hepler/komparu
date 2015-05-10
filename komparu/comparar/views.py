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


class Calculator:

    def __init__(self, apis):
        self.apis = apis

    def get_scores(self, a, b):
        results = []
        threads = []

        for api in self.apis:
            thread = threading.Thread(target=self.score_append, args=(results, api, a, b))
            threads.append(thread)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        a_product = self.get_item_product(results, a)
        b_product = self.get_item_product(results, b)

        return {a: a_product, b: b_product, "results": self.map_results(results)}

    def score_append(self, results, api, a, b):
        results.append(api.get_scores(a, b))

    def get_item_product(self, results, item):
        item_scores = [scores[1][item] for scores in results]

        for i, score in enumerate(item_scores):
            # shh no zeroes, only penalties now
            if score == 0.0:
                item_scores[i] = 0.5

        return reduce(operator.mul, item_scores, 1)

    def map_results(self, results):
        results_map = {}
        for scores in results:
            results_map[scores[0]] = {"scores": scores[1], "sanitized": scores[2]}
        return results_map



# API calls listed here:

class AngelListAPI:
    def get_scores(self, a, b):
        count_a = self.get_count(a)
        count_b = self.get_count(b)

        total = count_a + count_b

        score_a = self.get_score(total, count_a)
        score_b = self.get_score(total, count_b)

        # more startups means you're probably worse
        return "Angel List", {a: score_a, b: score_b}, {a: count_a, b: count_b}

    def get_count(self, item):
        response = unirest.get(
            "https://api.angel.co/1/search?query={0}&type=Startup".format(
                urllib.quote_plus(item))
        )

        results = response.body

        if not results:
            return 0
        else:
            # number of startups
            return len(results)

    def get_score(self, total, count):
        if total == 0:
            return 1.0

        return 1.0 - (count / total / 10.0)


class GenderGuesserAPI:
    def get_scores(self, a, b):
        gender_a = self.get_gender(a)
        gender_b = self.get_gender(b)

        score_a = self.get_score(gender_a)
        score_b = self.get_score(gender_b)
        return "Gender Guesser", {a: score_a, b: score_b}, {a: str(gender_a), b: str(gender_b)}

    def get_gender(self, item):
        response = unirest.get(
            "https://montanaflynn-gender-guesser.p.mashape.com/?name={0}".format(
                urllib.quote_plus(item)),
            headers={
                "X-Mashape-Key": "SuRl5yqxrrmsh4S2wAFlX9vmDWFUp1zg4Nsjsn9pi3WOXUUhwW",
                "Accept": "application/json"
            }
        )

        try:
            return response.body["gender"]
        except:
            # no gender response (or any error) means neutral
            return None

    def get_score(self, gender):
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
        count_a = self.get_pages(a)
        count_b = self.get_pages(b)

        score_a = self.get_score(count_a)
        score_b = self.get_score(count_b)

        # more pages, more better
        return "Google Books", {a: score_a, b: score_b}, {a: count_a, b: count_b}

    def get_pages(self, item):
        response = unirest.get(
            "https://www.googleapis.com/books/v1/volumes?q={0}&maxResults=40".format(
                urllib.quote_plus(item))
        )

        results = response.body

        if not results:
            return 0
        else:
            return sum(volume["volumeInfo"].get("pageCount", 0.0) for volume in results.get("items"))

    def get_score(self, count):
        return 1.0 + count / 10000.0


class GoogleResultsAPI:
    cats = float(134000000) # number of cats this metric finds

    def get_scores(self, a, b):
        results_a = self.get_results(a)
        results_b = self.get_results(b)

        score_a = GoogleResultsAPI.calculate_score(results_a)
        score_b = GoogleResultsAPI.calculate_score(results_b)

        return "Google Search", {a: score_a, b: score_b}, {a: results_a, b: results_b}

    @staticmethod
    def calculate_score(results):
        return (results - GoogleResultsAPI.cats) / GoogleResultsAPI.cats + 1

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
        count_a = self.get_count(a)
        count_b = self.get_count(b)

        total = count_a + count_b

        score_a = self.get_score(total, count_a)
        score_b = self.get_score(total, count_b)

        # the sanitized output here does not yet differentiate between synonyms and antonyms
        return "Thesaurus", {a: score_a, b: score_b}, {a: count_a, b: count_b}

    def get_count(self, item):
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

    def get_score(self, total, count):
        if total == 0:
            # this originally was 0.0, do I mean to change this or is it just 1:12am?
            return 1.0

        return 1.0 + (count * 1.0 / total)


class TweetSentimentAPI:
    def get_scores(self, a, b):
        score_a = self.get_score(a)
        score_b = self.get_score(b)

        # this sanitized output does not differ from the calculated score
        return "Twitter Sentiment", {a: score_a, b: score_b}, {a: score_a, b: score_b}

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
