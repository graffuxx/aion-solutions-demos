# CSV import validation

**Type:** synthetic data-quality demonstration with AI assistance.

## Failure

Treating identifiers as integers turns `00123` into `123`. A permissive import can also
accept duplicate records, impossible dates and invalid monetary values.

## Repair

[`validate()`](../../aion_demos/csv_validation.py) keeps identifiers as strings, uses
`Decimal` for amounts and checks an exact four-column schema. Valid rows and rejections
with source line numbers are returned separately.

```sh
python -m aion_demos csv-validation
```

Expected from [the fixture](../../sample-data/customer-import.csv): **2 accepted rows,
2 rejected rows**; `00123` retains its leading zeros. The source file is unchanged.

## Limits

Fixed CSV schema, not a universal Excel parser. Email validation checks shape only, not
mailbox ownership or deliverability. Duplicate detection uses accepted customer IDs
within one import; it does not query an external customer database.
