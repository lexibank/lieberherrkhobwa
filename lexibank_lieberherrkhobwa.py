from __future__ import unicode_literals, print_function

from clldutils.misc import slug
from clldutils.path import Path
from csvw.dsv import iterrows
from pylexibank.dataset import Dataset as BaseDataset

from language_mappings import MAPPINGS


class Dataset(BaseDataset):
    id = 'lieberherrkhobwa'
    dir = Path(__file__).parent

    def cmd_download(self, **kw):
        pass

    def cmd_install(self, **kw):
        data_ = self.raw / 'dataset.csv'

        with self.cldf as ds:
            for k, v in MAPPINGS.items():
                ds.add_language(ID=k, Name=k, Glottocode=v)

            language_index = {}
            meaning = None

            D = {0: ['doculect', 'concept', 'value', 'form']}



