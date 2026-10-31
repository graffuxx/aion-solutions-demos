# SQL debugging: inflated revenue

**Type:** synthetic SQLite debugging demonstration with AI assistance.

## Failure

A one-to-many join counts one order multiple times because it has multiple matching tags.
The fixture's actual matching revenue is 200 EUR, but the join produces 300 EUR.

## Repair

[`FIXED`](../../aion_demos/sql_debugging.py) uses `EXISTS` to select matching orders without
multiplying rows. Values are stored in integer cents.

```sh
python -m aion_demos sql-debugging
```

Expected: `broken_cents=30000`, `fixed_cents=20000`, `expected_cents=20000`.

## Limits

The example uses a tiny SQLite fixture, not a production database or performance benchmark.
Two separate orders may have equal amounts, so `SUM(DISTINCT amount)` would incorrectly
discard real revenue. SQL dialect, null handling and business rules still require review
before adapting the repair to a real database.
