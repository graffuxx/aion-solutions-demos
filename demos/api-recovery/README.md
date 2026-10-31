# API recovery and duplicate prevention

**Type:** synthetic, offline debugging demonstration with AI assistance.

## Failure

`broken_delivery()` tries once and fails on a simulated HTTP 503. A retry can also arrive
after the destination has stored an event but its response was lost.

## Repair

[`deliver()`](../../aion_demos/recovery.py) retries only transient errors, bounds the number
of attempts and uses a stable event ID. The simulated destination stores that ID as a
SQLite primary key and rejects reuse with a different payload.

```sh
python -m aion_demos api-recovery
```

Expected: 503, lost response after commit, then acceptance; **one destination row**.
The recorded backoff intervals are 1 and 2 seconds. The demo records these intervals
without sleeping, making execution deterministic and fast.

## Limits

This is not a live webhook server or HTTP client. Safe retries depend on destination-side
idempotency. Real integrations also need authentication, observability, jitter and
`Retry-After` handling. No general exactly-once guarantee is claimed.
