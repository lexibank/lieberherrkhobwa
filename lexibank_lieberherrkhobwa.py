from collections import OrderedDict

from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import NonSplittingDataset as BaseDataset

URL = (
    "https://zenodo.org/api/files/5469d550-938a-4dae-b6d9-50e427f193b3/"
    "metroxylon/subgrouping-kho-bwa-v1.0.0.zip"
)


class Dataset(BaseDataset):
    id = "lieberherrkhobwa"
    dir = Path(__file__).parent

    def cmd_download(self, **kw):
        self.raw.download_and_unpack(
            URL, "metroxylon-subgrouping-kho-bwa-333538b/data/dataset_khobwa.csv"
        )

    def split_forms(self, item, value):
        if value in self.lexemes:  # pragma: no cover
            self.log.debug('overriding via lexemes.csv: %r -> %r' % (value, self.lexemes[value]))
        value = self.lexemes.get(value, value)
        return [self.clean_form(item, form).strip()
                for form in split_text(value, separators='~/,;')]

    def cmd_install(self, **kw):

        data = self.raw.read_csv("dataset_khobwa.csv")
        assert set(len(r) for r in data) == {201}
        concept_by_index = OrderedDict()
        for i in range(1, len(data[0]), 2):
            concept_by_index[i] = data[0][i]

        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())

            # Read raw concept data and append it
            for concept in self.conceptlist.concepts.values():
                for i, gloss in list(concept_by_index.items()):
                    if gloss == concept.english:
                        concept_by_index[i] = concept.id
                        break
                else:
                    raise ValueError(concept["ENGLISH"])

                ds.add_concept(
                    ID=concept.id,
                    Name=concept.english,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss,
                )

            # Read raw languages and append it
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
                lid = slug(row[0])
                if lid in langs:
                    for cid in range(1, len(row), 2):
                        form = row[cid]
                        if not form or (form == "NA"):
                            continue
                        ipa = form
                        ipa = ipa.replace("- ", "-").replace(" ", "_")
                        ipa = strip_brackets(ipa).strip()

                        if ipa:
                            # split ipa and remove final/initial underscores if any
                            # (without regular expressions)
                            ipa = split_text(ipa, "~/~⪤,")[0]

                            if ipa[0] == "_":
                                ipa = ipa[1:].strip()
                            if ipa[-1] == "_":
                                ipa = ipa[:-1].strip()

                            # lingpy now requires this to be an integer
                            cognate_id = cid * 100 + int(row[cid + 1])

                            for lex in ds.add_lexemes(
                                Language_ID=lid,
                                Parameter_ID=concept_by_index[cid],
                                Value=form,
                                Form=ipa,
                                Cognacy=cognate_id,
                                Source=[langs[lid]],
                            ):
                                ds.add_cognate(
                                    lexeme=lex,
                                    Cognateset_ID=cognate_id,
                                    Source="Lieberherr2017",
                                    Alignment_Source="",
                                )
