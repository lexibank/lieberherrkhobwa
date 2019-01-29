# coding: utf-8
from __future__ import unicode_literals

from clldutils.jsonlib import load
from clldutils.path import Path


def test_zenodo_json():
    load(Path(__file__).parent / '.zenodo.json')


def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)

