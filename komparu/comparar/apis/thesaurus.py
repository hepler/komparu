import unirest
import urllib

class ThesaurusAPI:
    def get_scores(self, a, b):
        count_a = self.get_score(a)
        count_b = self.get_score(b)

        total = count_a + count_b
        ratio_a = count_a * 1.0 / total
        ratio_b = count_b * 1.0 / total

        return {a: 1.0 + ratio_a, b: 1.0 + ratio_b}

    def get_score(self, item):
        response = unirest.get(
            "http://words.bighugelabs.com/api/2/1992b053499e0716fe1b8308c5c40727/{0}/json".format(
                urllib.quote_plus(item)))

        if response.body:
            synonym_lists = self.get_all_lists(response.body, "syn")
            synonyms = sum(len(l) for l in synonym_lists)
            antonym_lists = self.get_all_lists(response.body, "ant")
            antonyms = sum(len(l) for l in antonym_lists)
        else:
            synonyms = 0
            antonyms = 0

        # the more haters you have, the more points you get
        return 2 * antonyms + synonyms

    def get_all_lists(self, body, key):
        lists = []
        for tense in body:
            if body[tense].get(key):
                lists.append(body[tense].get(key))
        return lists
