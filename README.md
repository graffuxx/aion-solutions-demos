# AI.on Solutions — Debugging Demos

Three small, runnable examples of repairing unreliable integrations and data workflows.
Created by Jan Ritter with AI assistance as synthetic portfolio demonstrations, not client work.

**Python standard library only. No API keys, network services or paid tools are required.**

| Demo | Reproduced problem | Repair and observable result |
| --- | --- | --- |
| [API recovery](demos/api-recovery/README.md) | A temporary HTTP failure, followed by a lost response after storage | Bounded retries with backoff and destination-side idempotency; one event stored once |
| [CSV validation](demos/csv-validation/README.md) | Lost leading zeros, duplicate identifiers and invalid dates | Preserve text IDs; accept 2 rows and reject 2 rows with reasons |
| [SQL debugging](demos/sql-debugging/README.md) | A one-to-many join inflates revenue | An `EXISTS` filter restores 200 EUR instead of 300 EUR |

## Run in a few minutes

Use Python 3.11 or newer. Run these commands from the repository root:

```sh
python -m aion_demos
python -m unittest discover -s tests -v
```

Some systems use `python3` instead of `python`. No package installation is needed.

Run one example:

```sh
python -m aion_demos api-recovery
python -m aion_demos csv-validation
python -m aion_demos sql-debugging
```

The runner prints structured JSON to your terminal. It uses in-memory SQLite and reads a
synthetic CSV fixture; it does not modify the source file or contact a real API.
See [expected output](docs/expected-results.json) for an inspectable reference.

## What the tests cover

The 20 regression tests cover transient and permanent API failures, exhausted retries,
lost responses after commit, persistence across restart, conflicting idempotency keys,
CSV schema and value validation, leading zeros, duplicate IDs and inflated SQL totals.
They also show why `SUM(DISTINCT amount)` is not a general repair for join duplication.

GitHub Actions runs the same tests and demo commands on Python 3.11, 3.12 and 3.13.
An actual workflow result, rather than this description, establishes the hosted CI status.

## Scope and authorship

- **Synthetic demos:** no customers, commercial deployments or production incidents are implied.
- **AI assistance:** code and documentation were prepared with AI assistance. The repository
  provides reproducible examples and their limitations; it does not imply unaided authorship.
- **No autonomous-learning claim:** these deterministic examples demonstrate software debugging,
  not machine learning or an autonomous AI system.
- **Confidential project excluded:** AION is a separate experimental personal project. Its
  architecture, components, source code and internal procedures are not in this repository.
- **No private material:** no course submissions, Zoom approval documents, credentials or
  customer datasets are included. Example email addresses use the reserved `.test` domain.

## Design choices and limitations

See [implementation notes](docs/design-notes.md) for the reasoning behind each repair and
what would still be required for a real integration.

This repository is maintained by **Jan Ritter / AI.on Solutions**.
