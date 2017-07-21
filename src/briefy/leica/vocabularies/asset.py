"""Asset vocabularies."""
from briefy.common.vocabularies import LabeledEnum


__all__ = (
    'AssetTypes',
)

asset_types = [
    ('Image', 'Photograph'),
    ('ImageRaw', 'Photograph (RAW)'),
    ('Image360', '360 degree Photograph'),
    ('Video', 'Video'),
    ('Cinemagraph', 'Cinemagraph'),
    ('Matterport', '3D Scan'),
]

AssetTypes = LabeledEnum('AssetTypes', asset_types)
