import unirest
import urllib

class ThesaurusAPI:
    def get_scores(self, a, b):
        count_a = self.get_count(a)
        count_b = self.get_count(b)

        total = count_a + count_b

        score_a = self.get_score(total, count_a)
        score_b = self.get_score(total, count_b)

        # the sanitized output here does not yet differentiate between synonyms and antonyms
        return "Thesaurus", {a: score_a, b: score_b}, {a: count_a, b: count_b}

    def get_count(self, item):
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

    def get_score(self, total, count):
        if total == 0:
            # this originally was 0.0, do I mean to change this or is it just 1:12am?
            return 1.0

        return 1.0 + (count * 1.0 / total)
