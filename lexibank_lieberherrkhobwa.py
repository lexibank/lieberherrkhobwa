"""
Module for installing the Lieberherr and Bodt (2017) dataset.
"""

import attr
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Language
from pylexibank.util import progressbar
from pylexibank import FormSpec


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
    form_spec = FormSpec(separators="~/,;⪤", missing_data=("NA",))

    def cmd_download(self, **kw):
        """
        Download the raw zipped data and extract it.
        """
        zip_url = (
            "https://zenodo.org/api/files/5469d550-938a-4dae-b6d9-50e427f193b3/"
            "metroxylon/subgrouping-kho-bwa-v1.0.0.zip"
        )
        filename = (
            "metroxylon-subgrouping-kho-bwa-333538b/data/dataset_khobwa.csv"
        )

        self.raw_dir.download(zip_url, "kho-bwa-v1.0.0.zip")

    def cmd_makecldf(self, args):
        # Add bibliographic sources
        args.writer.add_sources()

        # Read raw concept data and add to dataset; at the same time,
        # build a map between the concept index as used in data and the
        # concept id in the dataset
        concept_lookup = {}
        for cidx, concept in enumerate(self.conceptlists[0].concepts.values()):
            concept_cldf_id = (
                concept.id.split("-")[-1] + "_" + slug(concept.english)
            )
            concept_lookup[1 + (cidx * 2)] = concept_cldf_id

            # Add the concept
            args.writer.add_concept(
                ID=concept_cldf_id,
                Name=concept.english,
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
            )

        # Add languages and make a map for individual sources
        language_lookup = args.writer.add_languages(
            lookup_factory="Source_Name"
        )
        source_lookup = {
            entry["Source_Name"]: entry["Source"] for entry in self.languages
        }

        # Read raw data and remove headers and rows with reconstructions
        # (row[0] not in languages)
        data = self.raw_dir.read_csv("dataset_khobwa.csv")
        data = data[2:]
        data = [row for row in data if row[0] in language_lookup]

        # iterate over the source adding lexemes and collecting cognates
        for row in progressbar(data, desc="makecldf"):
            for cid in range(1, len(row), 2):
                # Skip over rows with empty fields for cogid
                if not row[cid + 1]:
                    continue

                # Compute a cognate_id number; lingpy now requires
                # this to be an integer
                cognate_id = cid * 100 + int(row[cid + 1])

                # Extract the value from the raw data, skipping over
                # missing or non-existing forms. We need to strip here,
                # as there are entries with newlines and FormSpec, as the
                # name implies, does not apply to values.
                value = row[cid].strip()
                for lex in args.writer.add_lexemes(
                    Language_ID=language_lookup[row[0]],
                    Parameter_ID=concept_lookup[cid],
                    Value=value,
                    Cognacy=cognate_id,
                    Source=source_lookup[row[0]],
                ):
                    args.writer.add_cognate(
                        lexeme=lex,
                        Cognateset_ID=cognate_id,
                        Source="Lieberherr2017",
                    )
