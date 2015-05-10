import unirest
import urllib

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
