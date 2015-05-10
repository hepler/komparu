import unirest
import urllib

import re

class TweetsAPI:
    count_re = re.compile(r'About ([0-9,]+) results')

    def get_scores(self, a, b):
        results_a = self.get_results(a)
        results_b = self.get_results(b)

        if results_a + results_b == 0:
            results_a = 0.000001
            results_b = 0.000001

        score_a = float(results_a) / (results_a + results_b) + 0.5
        score_b = float(results_b) / (results_a + results_b) + 0.5

        return "Twitter Activity", {a: score_a, b: score_b}, {a: results_a, b: results_b}

    @staticmethod
    def calculate_score(results):
        return 

    @staticmethod
    def get_results(item):
        site = 'site:twitter.com/*/status'
        url = 'https://www.google.com/search?q={}+{}'
        response = unirest.get(
            url.format(urllib.quote_plus(site), urllib.quote_plus(item)),
        )

        match = TweetsAPI.count_re.search(response.body)
        if (match):
            return int(match.group(1).replace(',', ''))
        else:
            return 0
