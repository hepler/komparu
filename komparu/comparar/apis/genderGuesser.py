import unirest
import urllib

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
