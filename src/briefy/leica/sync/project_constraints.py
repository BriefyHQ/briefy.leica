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

_agoda_constraints = {
    'set': {
        'minimum_number_of_photos': 10,
    },
    'asset': {
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
}

_aladina_constraints = {
    'set': {
        'minimum_number_of_photos': 10,
    },
    'asset': {
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
}

_beauty_constraints = {
    'set': {
        'minimum_number_of_photos': 10,
    },
    'asset': {
        'dimensions': [
            {
                'value': '2000x2000',
                'operator': 'min'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg
    }
}

_belvilla_constraints = {
    'set': {
        'minimum_number_of_photos': 40,
    },
    'asset': {
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
}

_auctionata_constraints = {
    'set': {
        'minimum_number_of_photos': 50,
    },
    'asset': {
        'dimensions': [
            {
                'value': '5205x3470',
                'operator': 'min'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_raw
    }
}

_eh_constraints = {
    'set': {
        'minimum_number_of_photos': 10,
    },
    'asset': {
        'dimensions': [
            {
                'value': '2000x2000',
                'operator': 'min'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg
    }
}

_ez_constraints = {
    'set': {
        'minimum_number_of_photos': 20,
    },
    'asset': {
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
}

_homeday_constraints = {
    'set': {
        'minimum_number_of_photos': 1,
    },
    'asset': {
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
}

_lovehome_constraints = {
    'set': {
        'minimum_number_of_photos': 20,
    },
    'asset': {
        'dimensions': [
            {
                'value': '800x450',
                'operator': 'min'
            },
        ],
        'mimetype': _is_jpeg
    }
}

_just_eat_constraints = {
    'set': {
        'minimum_number_of_photos': 12,
    },
    'asset': {
        'dimensions': [
            {
                'value': '4000x3000',
                'operator': 'eq'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg_or_png,
    }
}

_default_constraints = {
    'set': {
        'minimum_number_of_photos': 10,
    },
    'asset': {
        'dimensions': [
            {
                'value': '4000x3000',
                'operator': 'eq'
            },
        ],
        'orientation': _is_landscape,
        'mimetype': _is_jpeg_or_png,
    }
}


CONSTRAINTS = {
    'Agoda Bali': _agoda_constraints,
    'Agoda Bangkok': _agoda_constraints,
    'Agoda Pattaya': _agoda_constraints,
    'Agoda Phuket': _agoda_constraints,
    'Agoda Re-shoot / New shoot': _agoda_constraints,
    'Aladinia Spa Project (Pilot)': _default_constraints,
    'Aladinia': _aladina_constraints,
    'Auctionata': _auctionata_constraints,
    'Beauty Spotter Clinics': _beauty_constraints,
    'Beauty Spotter': _beauty_constraints,
    'Belvilla': _belvilla_constraints,
    'Classic Driver Pilot': _default_constraints,
    'Deliveroo Behind the Scene': _default_constraints,
    'Delivery Hero Cologne': _default_constraints,
    'Delivery Hero Hamburg': _default_constraints,
    'Delivery Hero Munich': _default_constraints,
    'Delivery Hero Pilot': _default_constraints,
    'eH Visio Clinics': _eh_constraints,
    'eH Visio': _eh_constraints,
    'Erento': _default_constraints,
    'Everphone Business Portrait': _default_constraints,
    'EZ cater': _ez_constraints,
    'ezCater USA': _ez_constraints,
    'Foodora Wien': _default_constraints,
    'Homeday Portraits': _homeday_constraints,
    'Homeday Properties': _homeday_constraints,
    'Just Eat finalists UK': _just_eat_constraints,
    'Leisure Group Belvilla DE': _default_constraints,
    'Leisure Group Belvilla ES': _default_constraints,
    'Leisure Group Belvilla FR': _default_constraints,
    'Leisure Group Belvilla IT': _default_constraints,
    'Love Home Swap': _lovehome_constraints,
    'Stayz Australia': _default_constraints,
    'WeTravel Yoga': _default_constraints,
}
