# encoding:utf-8

"""
Module for installing the Lieberherr and Bodt (2017) dataset.
"""

from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import NonSplittingDataset


class Dataset(NonSplittingDataset):
    """
    Defines the dataset for Lieberherr and Bodt (2017).
    """

    id = "lieberherrkhobwa"
    dir = Path(__file__).parent

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
            self.clean_form(item, form)
            for form in split_text(value, separators='~/,;')
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
            # build a map
            langs = {}
            for language in self.languages:
                langs[language["Name"]] = language["Source"]

                ds.add_language(
                    ID=language["Name"],
                    Name=language["Name"],
                    Glottocode=language["Glottocode"],
                    Glottolog_Name=language["Glottolog_Name"],
                )

            # iterate over the source adding lexemes and collecting cognates
            for row in data[2:]:
                # Get the language_id, which also allows to skip over
                # data we don't want
                lid = slug(row[0])

                if lid in langs:
                    for cid in range(1, len(row), 2):
                        # Extract the value from the raw data, skipping over
                        # missing or non-existing forms
                        value = row[cid].strip()
                        if not value or value == "NA":
                            continue

                        # Build the form, removing spaces between words
                        # in the same value and stripping brackets
                        form = value.replace("- ", "-").replace(" ", "_")
                        form = strip_brackets(form).strip()

                        if form:
                            # split form and remove final/initial underscores
                            # if any (without regular expressions)
                            form = split_text(form, "~/~⪤,")[0]
                            form = form.strip("_")

                            # lingpy now requires this to be an integer
                            cognate_id = cid * 100 + int(row[cid + 1])

                            for lex in ds.add_lexemes(
                                    Language_ID=lid,
                                    Parameter_ID=concept_by_index[cid],
                                    Value=value,
                                    Form=form,
                                    Cognacy=cognate_id,
                                    Source=[langs[lid]],
                            ):
                                ds.add_cognate(
                                    lexeme=lex,
                                    Cognateset_ID=cognate_id,
                                    Source="Lieberherr2017",
                                    Alignment_Source="",
                                )
