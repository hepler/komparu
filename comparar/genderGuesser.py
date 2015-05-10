import unirest
import urllib

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
