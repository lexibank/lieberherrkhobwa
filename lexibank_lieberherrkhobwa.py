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
        data = self.raw / 'dataset_khobwa.csv'

        with self.cldf as ds:
            for k, v in MAPPINGS.items():
                ds.add_language(ID=k, Name=k, Glottocode=v)

            language_index = {}
            meaning = None

            for i, row in enumerate(iterrows(data)):
                if i == 0:
                    for j, col in enumerate(row):
                        if (j > 1) and col:
                            language_index[j] = slug(col)
                elif i > 0:
                    if row[0].isdigit():
                        for j, col in enumerate(row):
                            if j == 1:
                                meaning = '{0}_l{1}'.format(slug(col), i + 1)
                                ds.add_concept(ID=meaning, Name=col)
                            elif j > 1:
                                ds.add_lexemes(
                                    Value=col,
                                    Language_ID=language_index[j],
                                    Parameter_ID=meaning
                                )
                    elif row[0].isdigit() is False:
                        # TODO: Take care manually of line 143, 'to run'.
                        # TODO: Take care manually of line 149, 'to say'.
                        print('Cognate Group')
