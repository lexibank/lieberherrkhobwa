from __future__ import unicode_literals, print_function

from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from csvw.dsv import iterrows
from pylexibank.dataset import Dataset as BaseDataset

from lingpy import *
from segments.tokenizer import Tokenizer

class Dataset(BaseDataset):
    id = 'lieberherrkhobwa'
    dir = Path(__file__).parent

    def cmd_download(self, **kw):
        pass

    def cmd_install(self, **kw):
        # Add forms in the way suggested by Mattis' in his implementation
        data = self.raw / 'data.tsv'
        raw_data = csv2list(data, strip_lines=False)

        # read the languages from the header
        languages = [slug(lang) for lang in raw_data[0]]

        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())

            # Read raw concept data and append it
            for concept in self.concepts:
                ds.add_concept(
                    ID=concept['CONCEPTICON_ID'],
                    Name=concept['ENGLISH'],
                    Concepticon_ID=concept['CONCEPTICON_ID'],
                    Concepticon_Gloss=concept['CONCEPTICON_GLOSS'],
                )
            concept2id = {
                c['ENGLISH'] : c['CONCEPTICON_ID'] for c in self.concepts
            }

            # Read raw languages and append it
            for language in self.languages:
                ds.add_language(
                    ID=language['ID'],
                    Name=language['Name'],
                    Glottocode=language['Glottocode'],
                    Glottolog_Name=language['Glottolog_Name'],
                )
            lang2id = {
                l['Name'] : l['ID'] for l in self.languages
            }

            # iterate over the source adding lexemes and collecting cognates
            for i in range(1, len(raw_data)-1, 2):
                tmp = dict(zip(languages, raw_data[i]))
                concept = raw_data[i][1]
                number = raw_data[i][0]

                for j, language in enumerate(languages[2:22]):
                    cog = raw_data[i+1][j+2]
                    form = tmp[language].strip()
                    modify = {"N": "N/ɴ", "’": "+"}
                    if form and form != 'NA':
                        ipa = form
                        ipa = ipa.replace('- ', '-').replace(' ', '_')
                        ipa = strip_brackets(ipa).strip()

                        if ipa:
                            # split ipa and remove final/initial underscores if any
                            # (without regular expressions)
                            ipa = split_text(ipa, '~/~⪤,')[0]

                            if ipa[0] == '_':
                                ipa = ipa[1:].strip()
                            if ipa[-1] == '_':
                                ipa = ipa[:-1].strip()

                            tks = [tok for tok in ipa2tokens(ipa) if tok != '_']
                            tks = [modify.get(x, x) for x in tks]

                            ipa = split_text(ipa, '~/~⪤,')[0]
                            tks = self.tokenizer(None, '^%s$' % ipa)

                            cognacy = '%s-%s' % (slug(concept), cog)

                            print(language, concept, cognacy)
                            print(form, ipa, tks)
                            print()

                        for row in ds.add_lexemes(
                            Language_ID=lang2id[language],
                            Parameter_ID=concept2id[concept],
                            Form=form,
                            Value=ipa,
                            Segments=tks,
                            Cognacy=cognacy,
                        ):
                            ds.add_cognate(
                                lexeme=row,
                                Cognateset_ID=cognacy,
                                Source='Lieberherr2017',
                                Alignment='',
                                Alignment_Source=''
                            )

            # align cognates
            ds.align_cognates()

        return

        # Automatically set the header, which is being stripped by the system...
        header_line = '#\tGloss\tDuhumbi\tKhispi\tRupa\tShergaon\tRahung\tKhoitam\tJerigaon\tKhoina\tDikhyang\tSingchung\tWangho\tBichom\tKaspi\tNamphri\tBulu\tKojo Rojo\tRawa\tSaria\tChayangtajo\tLasumpatte\tZMYYC\tLi Daqin\t\tʦB\tWB\tWT\tPT\tPBG\tPH\tPKC'
        header = header_line.split('\t')

        badcogs = '?'

        for i in range(0, len(raw_data)-1, 2):
            tmp = dict(zip(header, raw_data[i]))
            concept = raw_data[i][1]
            number = raw_data[i][0]

            import pprint
            pprint.pprint(tmp)
            print(list(enumerate(header[2:])))
            print(lmap)

            for j, language in enumerate(header[2:]):
                if slug(language) not in lmap:
                    continue

                cog = raw_data[i+1][j+2]
                form = tmp[language]
                if form.strip() and form.strip() != 'NA':
                    lang_id = lmap[slug(language)]
                    parameter_id = slug(concept)

                    ipa = form.replace('- ', '-')
                    ipa = ipa.split(' ~ ')[0].split('/')[0].split(',')[0]

                    tks = ipa2tokens(ipa.replace(' ', '_').replace('-',
                        '+').replace('*', ''))

                    cognacy = '%s-%s' % (concept, cog)

    #                print(lang_id, parameter_id, cognacy)
    #                print(form, ipa, tks)
    #                print()

#                    self.cldf.add_lexemes(
#                        Language_ID=lang_id,
#                        Parameter_ID=parameter_id,
#                        Form=form,
#                        Value=ipa,
#                        Segments=tks,
#                        Cognacy=cognacy,
#                    )
