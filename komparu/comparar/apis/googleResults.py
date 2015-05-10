import unirest
import urllib

class GoogleResults:
    cats = float(134000000) # number of cats this metric finds

    def get_scores(self, a, b):
        results_a = self.get_results(a)
        results_b = self.get_results(b)

        return {a: GoogleResults.calculate_score(results_a), b: GoogleResults.calculate_score(results_b)}

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
