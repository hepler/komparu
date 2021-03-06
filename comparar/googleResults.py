import unirest
import urllib

import re

class GoogleResultsAPI:
    count_re = re.compile(r'About ([0-9,]+) results')

    def get_scores(self, a, b):
        results_a = self.get_results(a)
        results_b = self.get_results(b)

        total = results_a + results_b

        score_a = GoogleResultsAPI.calculate_score(total, results_a)
        score_b = GoogleResultsAPI.calculate_score(total, results_b)

        return "Google Search", {a: score_a, b: score_b}, {a: results_a, b: results_b}

    @staticmethod
    def calculate_score(total, count):
        if total == 0:
            return 0.0

        return 1.0 + (count / 10.0 / total)

    @staticmethod
    def broken_get_results(item):
        url = 'https://www.googleapis.com/customsearch/v1?num=1&key=AIzaSyANy3-2kx-9_Mx8IlnuefRF-gQ17jZoMgE&cx=006715939817891416696:lc2hb0t40r0&q={}' 

        response = unirest.get(
            url.format(urllib.quote_plus(item)),
            headers={
                "Accept": "application/json"
            }
        )

        return int(response.body["searchInformation"]["totalResults"])

    @staticmethod
    def get_results(item):
        url = 'https://www.google.com/search?q={}'
        response = unirest.get(
            url.format(urllib.quote_plus(item)),
        )

        match = GoogleResultsAPI.count_re.search(response.body)
        if match:
            return int(match.group(1).replace(',', ''))
        else:
            return 0
