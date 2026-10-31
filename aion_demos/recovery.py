"""Synthetic API recovery demo. No real endpoints, credentials or customer data."""
import sqlite3

class HTTPError(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__(f'HTTP {status}')

class DemoAPI:
    """A simulated destination implementing durable idempotency keys."""
    def __init__(self, db, failures=()):
        self.db = db
        self.failures = iter(failures)
        db.execute('CREATE TABLE IF NOT EXISTS delivered (event_id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        db.commit()

    def send(self, event_id, payload):
        outcome = next(self.failures, 200)
        if outcome != 'timeout_after_commit' and outcome != 200:
            if outcome == 'timeout':
                raise TimeoutError('simulated timeout')
            raise HTTPError(outcome)
        old = self.db.execute('SELECT payload FROM delivered WHERE event_id=?', (event_id,)).fetchone()
        if old and old[0] != payload:
            raise HTTPError(409)
        self.db.execute('INSERT OR IGNORE INTO delivered VALUES (?,?)', (event_id, payload))
        self.db.commit()
        if outcome == 'timeout_after_commit':
            raise TimeoutError('response lost after destination committed')
        return {'event_id': event_id, 'accepted': True}


def broken_delivery(api, event_id, payload):
    return api.send(event_id, payload)  # Original defect: one attempt, no recovery.


def deliver(api, event_id, payload, attempts=4, sleep=lambda _: None):
    """Bounded retries, backoff, permanent-error handling, stable idempotency key.

    Real integration must honor Retry-After and use jitter; this deterministic
    offline demo deliberately models neither real rate limits nor a network.
    Safe retries depend on destination-side idempotency; they are not exactly-once
    delivery for arbitrary third-party APIs.
    """
    if not event_id or not isinstance(payload, str) or attempts < 1:
        raise ValueError('event ID, string payload and positive attempts required')
    log = []
    for attempt in range(attempts):
        try:
            result = api.send(event_id, payload)
            return {'result': result, 'log': log + [{'attempt': attempt + 1, 'status': 'accepted'}]}
        except (TimeoutError, HTTPError) as exc:
            retryable = isinstance(exc, TimeoutError) or exc.status in (429, 500, 502, 503, 504)
            log.append({'attempt': attempt + 1, 'status': str(exc), 'retryable': retryable})
            if not retryable or attempt + 1 == attempts:
                raise
            sleep(2 ** attempt)
