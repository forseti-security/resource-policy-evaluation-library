import pytest

from micromanager.resources import Resource
from micromanager.resources import BQDataset
from micromanager.resources import Bucket
from micromanager.resources import SQLInstance

test_cases = [
    (
        {'resource_kind': 'storage#bucket'},
        Bucket
    ),
    (
        {'resource_kind': 'sql#instance'},
        SQLInstance
    ),
    (
        {'resource_kind': 'bigquery#dataset'},
        BQDataset
    )
]


@pytest.mark.parametrize(
    "input,expected",
    test_cases,
    ids=[cls.__name__ for (_, cls) in test_cases])
def test_resource_factory(input, expected):
        r = Resource.factory(input)
        assert r.__class__ == expected

def test_resource_factory_invalid():
        with pytest.raises(AssertionError):
            r = Resource.factory({})
