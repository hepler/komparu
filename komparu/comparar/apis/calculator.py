import operator
import threading

class Calculator:

    def __init__(self, apis):
        self.apis = apis

    def get_scores(self, a, b):
        results = []
        threads = []

        for api in self.apis:
            thread = threading.Thread(target=self.score_append, args=(results, api, a, b))
            threads.append(thread)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        a_product = self.get_item_product(results, a)
        b_product = self.get_item_product(results, b)

        return {a: a_product, b: b_product}

    def score_append(self, results, api, a, b):
        results.append(api.get_scores(a, b))

    def get_item_product(self, results, item):
        item_scores = [scores[item] for scores in results]

        for i, score in enumerate(item_scores):
            # no zeroes, just penalties
            if score == 0.0:
                item_scores[i] = 0.5

        return reduce(operator.mul, item_scores, 1)