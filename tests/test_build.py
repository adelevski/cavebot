import copy
import json
from pathlib import Path
import pytest
from scripts.build import ROOT, build, validate_catalog

@pytest.fixture
def catalog():
    return json.loads((ROOT / 'data/caves.json').read_text())

@pytest.mark.parametrize('field,value', [('latitude', 91), ('longitude', float('nan')), ('depth_m', -1), ('length_km', True), ('latitude', 43.417)])
def test_rejects_invalid_measurements_or_precise_locations(catalog, field, value):
    catalog['caves'][0][field] = value
    with pytest.raises(ValueError):
        validate_catalog(catalog)

def test_rejects_duplicate_identity(catalog):
    catalog['caves'].append(copy.deepcopy(catalog['caves'][0]))
    with pytest.raises(ValueError, match='duplicate'):
        validate_catalog(catalog)

def test_rejects_unsafe_article_link(catalog):
    catalog['caves'][0]['wikipedia_url'] = 'javascript:alert(1)'
    with pytest.raises(ValueError, match='article URL'):
        validate_catalog(catalog)

def test_static_build_has_local_assets_and_provenance(tmp_path):
    output = build(tmp_path / 'site')
    page = (output / 'index.html').read_text()
    assert 'cave atlas' in page
    assert '__CATALOG__' not in page
    assert '1372337231' in page
    assert 'unpkg.com' not in page
    for asset in ['app.js', 'styles.css', 'vendor/leaflet.js', 'icon.png', 'favicon.png', 'caves.json', 'LICENSE', 'THIRD-PARTY-NOTICES.txt']:
        assert (output / asset).is_file()
