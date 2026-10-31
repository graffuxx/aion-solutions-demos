"""Synthetic CSV import repair, using only Python's standard library."""
import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

HEADER = ['customer_id', 'email', 'date', 'amount']


def broken_import(text):
    # Demonstrates two defects: loses leading zeros; binary-float money.
    return [(int(r['customer_id']), float(r['amount'])) for r in csv.DictReader(io.StringIO(text))]


def validate(text):
    reader = csv.DictReader(io.StringIO(text, newline=''))
    if reader.fieldnames != HEADER:
        raise ValueError('Expected exact columns: ' + ','.join(HEADER))
    accepted, rejected, seen = [], [], set()
    for line, row in enumerate(reader, 2):
        if None in row or any(v is None for v in row.values()):
            rejected.append({'line': line, 'reason': 'column_count', 'original': row})
            continue
        clean = {k: v.strip() for k, v in row.items()}
        reason = None
        if not all(clean.values()):
            reason = 'required_field'
        elif not (clean['customer_id'].isascii() and clean['customer_id'].isdigit()):
            reason = 'invalid_id'
        elif clean['email'].count('@') != 1 or any(c.isspace() for c in clean['email']) or not all(clean['email'].split('@')):
            reason = 'email_shape'  # Shape check only, not mailbox verification.
        else:
            try:
                value = datetime.strptime(clean['date'], '%Y-%m-%d')
                if value.strftime('%Y-%m-%d') != clean['date']:
                    raise ValueError()
            except ValueError:
                reason = 'invalid_date'
            if reason is None:
                try:
                    amount = Decimal(clean['amount'])
                    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal('0.01')):
                        raise InvalidOperation()
                    clean['amount'] = format(amount.quantize(Decimal('0.01')), 'f')
                except (InvalidOperation, ValueError):
                    reason = 'invalid_amount'
        if reason is None and clean['customer_id'] in seen:
            reason = 'duplicate_id'
        if reason:
            rejected.append({'line': line, 'reason': reason, 'original': row})
        else:
            seen.add(clean['customer_id'])
            accepted.append(clean)
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator='\n')
    writer.writeheader()
    writer.writerows(accepted)
    return {'accepted': accepted, 'rejected': rejected, 'csv': stream.getvalue()}
