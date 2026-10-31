# Design notes

## Keep the examples reproducible

All data is synthetic. SQLite runs in memory except for the temporary restart-persistence
test. There are no external dependencies, authentication steps or network calls.
Intentionally broken functions remain beside the repairs so the failure can be reproduced.

## Test behavior rather than implementation details

The tests assert observable outcomes: row counts, preserved identifiers, rejection reasons,
retry limits and accurate revenue totals. The timeout-after-commit case demonstrates why
retry logic without a destination-side idempotency contract can duplicate side effects.

## Deliberately limited scope

The demos omit real networking, distributed concurrency, production monitoring and large
dataset benchmarks. They are learning and portfolio artifacts, not production certification.
Existing test evidence should not be interpreted as proof of suitability for an arbitrary
client system. Each use requires its own acceptance criteria.

## Public boundary

This repository contains only the three synthetic demonstrations. It includes no AION
implementation, study-folder audit, private project paths, contact directory, original
coursework datasets, Zoom credentials or approval files.
