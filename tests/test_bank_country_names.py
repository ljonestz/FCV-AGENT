"""Official inverted country names remain single beneficiaries, not false pairs."""

import pytest

from sector_lenses.climate_verified_runtime import extract_beneficiary_countries


@pytest.mark.parametrize('value,expected', [
    ('Egypt, Arab Rep.', ('Egypt, Arab Rep.',)),
    ('Iran, Islamic Rep.', ('Iran, Islamic Rep.',)),
    ('Gambia, The', ('Gambia, The',)),
    ('Egypt, Arab Republic of', ('Egypt, Arab Republic of',)),
    ('Egypt, Arab Rep., Jordan', ('Egypt, Arab Rep.', 'Jordan')),
    ('Senegal, The Gambia', ('Senegal', 'The Gambia')),
    ('Iran, Iraq', ('Iran', 'Iraq')),
    ('Congo, Democratic Republic of; Congo, Republic of',
     ('Congo, Democratic Republic of', 'Congo, Republic of')),
    ('Venezuela, RB; Micronesia, Fed. Sts.', ('Venezuela, RB', 'Micronesia, Fed. Sts.')),
])
def test_official_names_and_actual_multicountry_fields(value, expected):
    assert extract_beneficiary_countries('Beneficiary Country/Countries\n' + value + '\n') == expected
