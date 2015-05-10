import unirest
import urllib

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
