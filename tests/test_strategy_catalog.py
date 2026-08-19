from pathlib import Path
from arthashree.strategy_registry import StrategyRegistry
from arthashree.catalog import CatalogService, CatalogEntry


def test_register_from_path_and_catalog(tmp_path):
    reg = StrategyRegistry()
    # register from module path
    reg.register_from_path('example', 'arthashree.strategies.example_strategy')
    assert 'example' in reg.list()

    # ensure metadata includes module_path and class_name
    meta = reg.metadata('example')
    assert meta is not None
    assert meta.get('module_path') == 'arthashree.strategies.example_strategy'
    assert meta.get('class_name') == 'ExampleStrategy'

    # test CatalogService persistence
    catalog_file = tmp_path / 'catalog.json'
    cs = CatalogService(catalog_file)
    entry = CatalogEntry(name='example', module_path='arthashree.strategies.example_strategy', class_name='ExampleStrategy', version='0.1')
    cs.register(entry)
    loaded = CatalogService(catalog_file)
    e = loaded.get('example')
    assert e is not None
    assert e.module_path == 'arthashree.strategies.example_strategy'
