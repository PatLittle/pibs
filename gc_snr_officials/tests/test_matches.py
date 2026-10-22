import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_matches import build, nickname_lookup, relation, score_pair
from names import normalize_name


def record(name, org='Agency', role='Director', first='2020-01-01', last='2021-01-01'):
    return dict(**normalize_name(name), owner_org_title=org, title_en=role, observed_from=first, observed_to=last)


class Matches(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/nicknames.csv').open() as f:
            cls.lookup = nickname_lookup(list(csv.DictReader(f)))

    def test_compact_names_and_preserved_forms(self):
        r = normalize_name('Smith,\tJames A.\nB.')
        self.assertEqual(r['name'], 'JamesABSmith')
        self.assertEqual(r['name_normalized'], 'James A. B. Smith')
        self.assertEqual(r['name_original'], 'Smith,\tJames A.\nB.')
        self.assertEqual(normalize_name('Jean\u00a0Smith')['name'], 'JeanSmith')

    def test_lookup_examples_and_no_transitive_closure(self):
        for a, b in [('james', 'jim'), ('james', 'jimmy'), ('jim', 'jimmy'), ('deborah', 'debby'), ('debby', 'debbie')]:
            self.assertIsNotNone(relation(a, b, self.lookup), (a, b))
        lookup = nickname_lookup([dict(name1='a', relationship='has_nickname', name2='b'), dict(name1='b', relationship='has_nickname', name2='c')])
        self.assertIsNone(relation('a', 'c', lookup))
        self.assertFalse(build([record('James Smith'), record('Jim Jones')], self.lookup))

    def test_institution_roles_dates_and_missing_access_dates(self):
        a = [record('James Smith')]
        similar = score_pair(a, [record('Jim Smith')], 'direct nickname', 60)
        sequential = score_pair(a, [record('Jim Smith', 'Other', 'Chief', '2022-01-01', '2023-01-01')], 'direct nickname', 60)
        overlapping = score_pair(a, [record('Jim Smith', 'Other', 'Chief')], 'direct nickname', 60)
        self.assertGreater(similar['score'], sequential['score'])
        self.assertGreater(sequential['score'], overlapping['score'])
        self.assertEqual(overlapping['score'], 60)
        missing = dict(record('Jim Smith', 'Other', 'Chief', '', ''), source_date='2020-01-01')
        self.assertEqual(score_pair(a, [missing], 'direct nickname', 60)['score'], 60)

    def test_middle_names_conflict_and_benay_transition(self):
        a = [record('James Alan Smith')]
        self.assertLessEqual(score_pair(a, [record('Jim Brian Smith')], 'direct nickname', 60)['score'], 49)
        self.assertGreater(score_pair(a, [record('Jim A. Smith')], 'direct nickname', 60)['score'], 80)
        a = [record('Alexandre Benay', 'TBS', 'CIO', '2018-02-16', '2019-07-05')]
        b = [record('Alex Benay', 'PSPC', 'Associate Deputy Minister', '2023-07-04', '2026-03-21')]
        score = score_pair(a, b, 'direct nickname', 60)
        self.assertEqual(score['score'], 70)
        a += [record('Alexandre Benay', 'PSPC', 'Associate Deputy Minister', '2024-09-23', '2024-09-27')]
        self.assertEqual(score_pair(a, b, 'direct nickname', 60)['score'], 95)


if __name__ == '__main__':
    unittest.main()
