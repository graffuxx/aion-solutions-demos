"""Run the three demonstrations without network access or third-party packages."""
import argparse
import json
import sqlite3
from pathlib import Path

from .csv_validation import validate
from .recovery import DemoAPI, deliver
from .sql_debugging import compare


def run(name):
    if name == 'api-recovery':
        with sqlite3.connect(':memory:') as db:
            delays = []
            api = DemoAPI(db, [503, 'timeout_after_commit'])
            result = deliver(api, 'demo-001', 'synthetic order', sleep=delays.append)
            result['destination_rows'] = db.execute('SELECT COUNT(*) FROM delivered').fetchone()[0]
            result['backoff_seconds'] = delays
            return result
    if name == 'csv-validation':
        path = Path(__file__).resolve().parent.parent / 'sample-data/customer-import.csv'
        result = validate(path.read_text(encoding='utf-8'))
        return {'accepted_rows': len(result['accepted']),
                'rejected_rows': len(result['rejected']),
                'accepted': result['accepted'], 'rejected': result['rejected'],
                'clean_csv': result['csv']}
    return compare()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('demo', choices=['all', 'api-recovery', 'csv-validation', 'sql-debugging'],
                        nargs='?', default='all')
    args = parser.parse_args()
    names = ['api-recovery', 'csv-validation', 'sql-debugging'] if args.demo == 'all' else [args.demo]
    print(json.dumps({'label': 'Synthetic demonstrations; not client work',
                      'demos': {name: run(name) for name in names}}, indent=2))


if __name__ == '__main__':
    main()
