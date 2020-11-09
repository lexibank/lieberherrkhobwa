# encoding:utf-8

"""
Module for installing the Lieberherr and Bodt (2017) dataset.
"""

import attr
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.models import Language

@attr.s
class KBLanguage(Language):
    Source = attr.ib(default=None)
    Source_Name = attr.ib(default=None)


class Dataset(BaseDataset):
    """
    Defines the dataset for Lieberherr and Bodt (2017).
    """

    id = "lieberherrkhobwa"
    dir = Path(__file__).parent
    language_class = KBLanguage

    def cmd_download(self, **kw):
        """
        Download the raw zipped data and extract it.
        """
        zip_url = (
            "https://zenodo.org/api/files/5469d550-938a-4dae-b6d9-50e427f193b3/"
            "metroxylon/subgrouping-kho-bwa-v1.0.0.zip"
        )
        filename = "metroxylon-subgrouping-kho-bwa-333538b/data/dataset_khobwa.csv"

        self.raw.download_and_unpack(zip_url, filename)


    def split_forms(self, item, value):
        """
        Splits and cleans forms before passing them to the tokenizer.
        """

        # Inform that the value is being overriden
        if value in self.lexemes:  # pragma: no cover
            self.log.debug('overriding via lexemes.csv: %r -> %r' %
                           (value, self.lexemes[value]))

        # Get the replacement value for `lexemes.csv`
        value = self.lexemes.get(value, value)

        # Return a list of cleaned forms, splitting over tilde, slash,
        # comma, and colon
        forms = [
            self.clean_form(item, form).strip()
            for form in split_text(value, separators='~/,;⪤')
        ]

        return forms


    def cmd_install(self, **kw):
        # Read the raw data
        data = self.raw.read_csv("dataset_khobwa.csv")

        with self.cldf as ds:
            # Add bibliographic sources
            ds.add_sources(*self.raw.read_bib())

            # Read raw concept data and add to dataset; at the same time,
            # build a map between the concept index in data and the
            # concept id in the dataset
            concept_by_index = {}
            for cid, concept in enumerate(self.conceptlist.concepts.values()):
                # We can get the concept id from the raw data
                concept_by_index[1+(cid*2)] = concept.id

                # Add the concept
                ds.add_concept(
                    ID=concept.id,
                    Name=concept.english,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss,
                )

            # Read raw languages and add to the dataset; at the same time,
            # build a map that can be used for iterating over language ids
            langs = {
                l['Source_Name']: {'id': l['ID'], 'source': l['Source']}
                for l in self.languages
            }
            ds.add_languages()

            # iterate over the source adding lexemes and collecting cognates
            for row in data[2:]:
                # Confirm the row refers to one of the languages to be
                # included (i.e., no reconstructions)
                if row[0] in langs:
                    for cid in range(1, len(row), 2):
                        # Skip over rows with empty fields for cogid
                        if not row[cid+1]:
                            continue

                        # Compute a cognate_id number; lingpy now requires
                        # this to be an integer
                        cognate_id = cid * 100 + int(row[cid + 1])

                        # Extract the value from the raw data, skipping over
                        # missing or non-existing forms
                        value = row[cid].strip()
                        if value != "NA":
                            for lex in ds.add_lexemes(
                                    Language_ID=langs[row[0]]['id'],
                                    Parameter_ID=concept_by_index[cid],
                                    Value=value,
                                    Cognacy=cognate_id,
                                    Source=langs[row[0]]['source'],
                            ):
                                ds.add_cognate(
                                    lexeme=lex,
                                    Cognateset_ID=cognate_id,
                                    Source="Lieberherr2017",
                                    Alignment_Source="",
                                )
