"""Project constraints.

Imported from Ms. Laure.
"""

_is_jpeg = [
    {'value': 'image/jpeg', 'operator': 'eq'},
]

_is_jpeg_or_png = [
    {'value': ['image/jpeg', 'image/png'], 'operator': 'in'},
]


_is_raw = [
    {'value': 'image/tiff', 'operator': 'eq'},
]

_is_landscape = [{'value': 'landscape', 'operator': 'eq'}]
_is_portrait = [{'value': 'portrait', 'operator': 'eq'}]

_agoda_constraints = (
    10,
    {
        'dimensions': [
            {
                'value': '4150x3100',
                'operator': 'min'
            },
            {
                'value': '4250x3200',
                'operator': 'max'
            },
        ],
        'orientation': _is_landscape,
        'ratio': [
            {
                'value': 4 / 3,
                'operator': 'eq'
            },
        ],
        'mimetype': _is_jpeg
    }
)

_aladina_constraints = (
    10,
    {
        'dimensions': [
            {
                'value': '780x780',
                'operator': 'min'
            },
            {
                'value': '820x820',
                'operator': 'max'
            },
        ],
        'ratio': [
            {
                'value': 1,
                'operator': 'eq'
            },
        ],
        'mimetype': _is_jpeg
    }
)

_beauty_constraints = (
    10,
    {
        'dimensions': [
            {
                'value': '2000x2000',
                'operator': 'min'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg
    }
)

_belvilla_constraints = (
    40,
    {
        'dimensions': [
            {
                'value': '3822x2854',
                'operator': 'min'
            },
            {
                'value': '3922x2954',
                'operator': 'max'
            },
        ],
        'orientation': _is_landscape,
        'ratio': [
            {
                'value': 4 / 3,
                'operator': 'eq'
            },
        ],
        'mimetype': _is_jpeg
    }
)

_auctionata_constraints = (
    50,
    {
        'dimensions': [
            {
                'value': '5205x3470',
                'operator': 'min'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_raw
    }
)

_eh_constraints = (
    10,
    {
        'dimensions': [
            {
                'value': '2000x2000',
                'operator': 'min'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg
    }
)

_ez_constraints = (
    20,
    {
        'dimensions': [
            {
                'value': '2950x2200',
                'operator': 'min'
            },
            {
                'value': '3050x2300',
                'operator': 'max'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg
    }
)

_homeday_constraints = (
    1,
    {
        'dimensions': [
            {
                'value': '2313x3494',
                'operator': 'min'
            },
            {
                'value': '2413x3594',
                'operator': 'max'
            },
        ],
        'ratio': [
            {
                'value': 2 / 3,
                'operator': 'eq'
            },
        ],
        'orientation': _is_portrait,
        'mimetype': _is_jpeg
    }
)

_lovehome_constraints = (
    20,
    {
        'dimensions': [
            {
                'value': '800x450',
                'operator': 'min'
            },
        ],
        'mimetype': _is_jpeg
    }
)

_just_eat_constraints = (
    12,
    {
        'dimensions': [
            {
                'value': '4000x3000',
                'operator': 'eq'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg_or_png,
    }
)

_default_constraints = (
    10,
    {
        'dimensions': [
            {
                'value': '4000x3000',
                'operator': 'eq'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg_or_png,
    }
)


CONSTRAINTS = {
    'Agoda Bali': _agoda_constraints[1],
    'Agoda Bangkok': _agoda_constraints[1],
    'Agoda Pattaya': _agoda_constraints[1],
    'Agoda Phuket': _agoda_constraints[1],
    'Agoda Re-shoot / New shoot': _agoda_constraints[1],
    'Aladinia Spa Project (Pilot)': _default_constraints[1],
    'Aladinia': _aladina_constraints[1],
    'Auctionata': _auctionata_constraints[1],
    'Beauty Spotter Clinics': _beauty_constraints[1],
    'Beauty Spotter': _beauty_constraints[1],
    'Belvilla': _belvilla_constraints[1],
    'Classic Driver Pilot': _default_constraints[1],
    'Deliveroo Behind the Scene': _default_constraints[1],
    'Delivery Hero Pilot': _default_constraints[1],
    'eH Visio Clinics': _eh_constraints[1],
    'eH Visio': _eh_constraints[1],
    'Erento': _default_constraints[1],
    'Everphone Business Portrait': _default_constraints[1],
    'EZ cater': _ez_constraints[1],
    'ezCater USA': _ez_constraints[1],
    'Foodora Wien': _default_constraints[1],
    'Homeday Portraits': _homeday_constraints[1],
    'Homeday Properties': _homeday_constraints[1],
    'Just Eat finalists UK': _just_eat_constraints[1],
    'Leisure Group Belvilla DE': _default_constraints[1],
    'Leisure Group Belvilla ES': _default_constraints[1],
    'Leisure Group Belvilla FR': _default_constraints[1],
    'Leisure Group Belvilla IT': _default_constraints[1],
    'Love Home Swap': _lovehome_constraints[1],
    'Stayz Australia': _default_constraints[1],
    'WeTravel Yoga': _default_constraints[1],
}
