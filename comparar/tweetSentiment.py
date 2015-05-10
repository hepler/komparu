import unirest
import urllib
import math

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
