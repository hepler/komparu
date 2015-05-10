import unirest
import urllib

class AngelListAPI:
    def get_scores(self, a, b):
        count_a = self.get_score(a)
        count_b = self.get_score(b)

        total = count_a + count_b
        adjusted_ratio_a = count_a * 1.0 / total / 10
        adjusted_ratio_b = count_b * 1.0 / total / 10

        # more startups means you're probably worse
        return {a: 1.0 - adjusted_ratio_a, b: 1.0 - adjusted_ratio_b}

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

