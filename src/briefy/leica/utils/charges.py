"""OrderCharge helpers."""
from briefy.leica.utils.date import utc_now_serialized
from briefy.ws.errors import ValidationError
from datetime import date
from uuid import uuid4

import typing as t


_FIELDS = ('category', 'amount', 'invoice_number', 'invoice_date', 'reason')


def order_charges_update(current_value: t.Sequence, new_value: t.Sequence) -> t.Sequence:
    """Function to handle OrderCharges modification.

    :param current_value: Current OrderCharges.
    :param new_value: New OrderCharges.
    :return: OrderCharges to be persisted.
    """
    processed = []
    current_dict = {line['id']: line for line in current_value}
    to_update = {line['id']: line for line in new_value if line.get('id') in current_dict}
    to_delete = {k: v for k, v in current_dict.items() if k not in to_update}

    # Validate if we can delete
    for key in to_delete:
        line = to_delete[key]
        invoice_number = line.get('invoice_number')
        invoice_date = line.get('invoice_date')
        if invoice_date and invoice_number:
            raise ValidationError(
                'Not possible to delete an already invoiced item.', name='additional_charges'
            )

    for line in new_value:
        line_id = line.get('id')
        invoice_date = line.get('invoice_date')
        if isinstance(invoice_date, date):
            line['invoice_date'] = invoice_date.isoformat()
        if line_id not in to_update:
            line['created_at'] = utc_now_serialized()
            if not line_id:
                line['id'] = str(uuid4())
            current_item = line
        else:
            current_item = current_dict[line_id]
            for field in _FIELDS:
                current_item[field] = line[field]
        processed.append(current_item)

    return processed
