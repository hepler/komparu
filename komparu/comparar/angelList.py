import unirest
import urllib

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
