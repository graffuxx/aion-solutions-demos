import sqlite3
import tempfile
import unittest
from pathlib import Path
from aion_demos.recovery import DemoAPI, HTTPError, broken_delivery, deliver
from aion_demos.csv_validation import validate, broken_import
from aion_demos.sql_debugging import fixture, compare, FIXED

PREFIX = 'customer_id,email,date,amount\n'
GOOD = '00123,jan@example.test,2026-10-31,12.30\n'

class RecoveryTests(unittest.TestCase):
    def api(self, failures=()):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        return DemoAPI(db, failures)
    def test_original_failure(self):
        with self.assertRaises(HTTPError): broken_delivery(self.api([503]), 'x', 'sample')
    def test_transient_and_backoff(self):
        delays = []
        result = deliver(self.api([503,429]), 'x', 'sample', sleep=delays.append)
        self.assertEqual(delays,[1,2])
        self.assertEqual(len(result['log']),3)
    def test_timeout_after_commit(self):
        api = self.api(['timeout_after_commit'])
        deliver(api,'x','sample')
        self.assertEqual(api.db.execute('SELECT COUNT(*) FROM delivered').fetchone()[0],1)
    def test_permanent_failure(self):
        api = self.api([401,200])
        with self.assertRaises(HTTPError): deliver(api,'x','sample')
        self.assertEqual(api.db.execute('SELECT COUNT(*) FROM delivered').fetchone()[0],0)
    def test_exhausted(self):
        with self.assertRaises(HTTPError): deliver(self.api([503]*4),'x','sample')
    def test_conflict(self):
        api = self.api()
        deliver(api,'x','one')
        with self.assertRaises(HTTPError): deliver(api,'x','two')
    def test_restart_preserves_idempotency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'demo.db'
            with sqlite3.connect(path) as db: deliver(DemoAPI(db),'x','sample')
            with sqlite3.connect(path) as db:
                deliver(DemoAPI(db),'x','sample')
                self.assertEqual(db.execute('SELECT COUNT(*) FROM delivered').fetchone()[0],1)
    def test_invalid_attempts(self):
        with self.assertRaises(ValueError): deliver(self.api(),'x','sample',attempts=0)

class CSVTests(unittest.TestCase):
    def test_original_loses_identifier(self):
        self.assertEqual(broken_import(PREFIX+GOOD)[0][0],123)
    def test_preserves_identifier(self):
        self.assertEqual(validate(PREFIX+GOOD)['accepted'][0]['customer_id'],'00123')
    def test_duplicate(self):
        result=validate(PREFIX+GOOD+GOOD)
        self.assertEqual(len(result['accepted']),1)
        self.assertEqual(result['rejected'][0]['reason'],'duplicate_id')
    def test_invalid_values(self):
        for value,reason in [('1,,2026-10-31,1','required_field'),('1,a@b,2026-02-30,1','invalid_date'),('1,a@b,2026-10-31,NaN','invalid_amount'),('1,a@b,2026-10-31,1.001','invalid_amount'),('1,a@b,2026-10-31,-1','invalid_amount'),('1,a @b,2026-10-31,1','email_shape')]:
            with self.subTest(value=value):
                self.assertEqual(validate(PREFIX+value+'\n')['rejected'][0]['reason'],reason)
    def test_wrong_columns(self):
        with self.assertRaises(ValueError): validate('id,email\n1,a@b\n')
    def test_extra_column(self):
        self.assertEqual(validate(PREFIX+GOOD.strip()+',extra\n')['rejected'][0]['reason'],'column_count')
    def test_missing_column(self):
        self.assertEqual(validate(PREFIX+'1,a@b\n')['rejected'][0]['reason'],'column_count')
    def test_idempotent(self):
        once=validate(PREFIX+GOOD)['csv']
        self.assertEqual(validate(once)['csv'],once)
    def test_source_unchanged(self):
        source=PREFIX+GOOD
        validate(source)
        self.assertEqual(source,PREFIX+GOOD)

class SQLTests(unittest.TestCase):
    def test_bug_and_repair(self):
        self.assertEqual(compare(),{'broken_cents':30000,'fixed_cents':20000,'expected_cents':20000})
    def test_distinct_amount_is_not_fix(self):
        with fixture() as db:
            self.assertEqual(db.execute('SELECT SUM(DISTINCT cents) FROM orders WHERE id IN (1,2)').fetchone()[0],10000)
    def test_duplicate_tags(self):
        with fixture() as db:
            db.execute("INSERT INTO tags VALUES(2,'api')")
            self.assertEqual(db.execute(FIXED).fetchone()[0],20000)

if __name__=='__main__': unittest.main(verbosity=2)
