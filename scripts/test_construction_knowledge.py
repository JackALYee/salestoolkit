"""Construction source ingestion, answer downloads and authenticated originals.

Run with the site's Python dependencies. No network, production DB or AI calls.
"""
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ['AUTH_SECRET'] = 'construction-test-only'
os.environ['JERRY_LEARN_ENABLED'] = '0'
import server as S
import downloads as D
from learning import engine as E
from fastapi.testclient import TestClient

SOURCES = ROOT / 'jerry_gpt_knowledge' / 'Construction vehicle solutions'
IDS = [a['id'] for a in D.CONSTRUCTION_ASSETS]


class ConstructionKnowledge(unittest.TestCase):
    def client(self, user=None):
        c = TestClient(S.app)
        if user:
            c.cookies.set(S.COOKIE_NAME, S.make_token(user))
        return c

    def test_english_chinese_and_followup_document_triggers(self):
        for text in (
            'Explain construction vehicle visibility options and all BOMs.',
            'For our excavators compare two, four and five camera wiring.',
            '工程车辆可视化方案：五路摄像头怎么接线？',
            '请介绍装载机盲区方案并提供三份文档',
            'C09: which camera bypasses the switch?',
            'Here are the construction vehicle solutions documents you requested.',
            '03_Technical_Compatibility_and_Validation_Matrix.xlsx',
        ):
            with self.subTest(text=text):
                self.assertEqual([d['id'] for d in D.find_downloads(text)], IDS)

    def test_complete_set_has_priority_over_incidental_topics(self):
        result = D.find_downloads('Construction vehicle solutions: CAN bus, eSIM, DPA and privacy masking')
        self.assertEqual([d['id'] for d in result[:3]], IDS)
        self.assertLessEqual(len(result), D.MAX_DOWNLOADS)
        self.assertEqual(len({d['id'] for d in result}), len(result))

    def test_generic_visibility_and_construction_of_software_are_not_matches(self):
        for text in ('How does C46 blind-spot detection work?',
                     'Construction of a website requires software.',
                     'Compare fuel theft and dashcams.', 'What is AC090?'):
            with self.subTest(text=text):
                self.assertFalse(set(IDS) & {d['id'] for d in D.find_downloads(text)})

    def test_response_extras_scan_question_and_use_private_routes(self):
        result = S._response_extras('Start with the monitored hazard zones.',
                                    'Construction vehicle visibility: full BOM and drawings?')
        self.assertEqual([d['url'] for d in result['downloads']],
                         [f'/api/jerry/documents/{i}' for i in IDS])

    def test_original_bytes_mime_filename_and_all_user_access(self):
        manifest = json.loads((SOURCES / 'source-manifest.json').read_text())
        hashes = {d['filename']: d['sha256'] for d in manifest['documents']}
        self.assertEqual(len(hashes), 3)
        for user in ('kiki@streamax.com', 'jimmy@streamax.com', 'jcyi@streamax.com'):
            for asset in D.CONSTRUCTION_ASSETS:
                with self.subTest(user=user, asset=asset['id']):
                    r = self.client(user).get(f"/api/jerry/documents/{asset['id']}")
                    self.assertEqual(r.status_code, 200)
                    self.assertEqual(hashlib.sha256(r.content).hexdigest(), hashes[asset['filename']])
                    self.assertEqual(r.headers['content-type'], asset['mime'])
                    self.assertIn('attachment;', r.headers['content-disposition'])
                    self.assertIn(asset['filename'], r.headers['content-disposition'])
                    self.assertEqual(r.headers['cache-control'], 'private, no-store')

    def test_anonymous_unknown_and_public_path_are_denied(self):
        for asset in D.CONSTRUCTION_ASSETS:
            self.assertEqual(self.client().get(f"/api/jerry/documents/{asset['id']}").status_code, 401)
            self.assertEqual(self.client().get('/assets/downloads/' + asset['filename']).status_code, 404)
        self.assertEqual(self.client('kiki@streamax.com').get('/api/jerry/documents/source-manifest.json').status_code, 404)
        self.assertIsNone(D.construction_document('../00_jerry_persona.md'))
        self.assertIsNone(D.construction_document('construction_bom/../../server.py'))

    def test_knowledge_is_loaded_and_maintainer_memory_is_excluded(self):
        blocks = S._jerry._load_system_blocks()
        text = '\n'.join(b['text'] for b in blocks)
        self.assertIn('<knowledge file="27_construction_vehicle_solutions.md">', text)
        self.assertIn('one direct IPC + four through one switch', text)
        self.assertIn('1261050100539 is included in both', text)
        self.assertIn('DEBUG filename does not prove approved mass-production release', text)
        self.assertNotIn('<knowledge file="sub-memory.md">', text)
        self.assertNotIn('<knowledge file="memory.md">', text)

    def test_daily_learning_can_ground_construction_claims_in_curated_source(self):
        evidence = E.curated_evidence([{'question': 'Construction C09 M1N five cameras one direct IPC four switch 5173002100003'}])
        self.assertTrue(any('27_construction_vehicle_solutions.md' in str(e) for e in evidence))
        self.assertFalse(any('sub-memory.md' in str(e) for e in evidence))


if __name__ == '__main__':
    unittest.main()
