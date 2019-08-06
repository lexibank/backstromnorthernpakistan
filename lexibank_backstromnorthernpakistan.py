import attr
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.dataset import Concept, Language
from tqdm import tqdm
import csv


@attr.s
class Language(Language):
    Source_ID = attr.ib(default=None)
    Name = attr.ib(default=None)
    Glottolog_Name = attr.ib(default=None)
    Glottocode = attr.ib(default=None)
    ISO639P3code = attr.ib(default=None)
    List_ID = attr.ib(default=None)
    List_Name = attr.ib(default=None)
    Family = attr.ib(default=None)
    Location = attr.ib(default=None)
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    Note = attr.ib(default=None)

@attr.s
class Concept(Concept):
    ENGLISH = attr.ib(default=None)


class Dataset(BaseDataset):
    id = 'backstromnorthernpakistan'
    dir = Path(__file__).parent
    concept_class = Concept
    language_class = Language

    def cmd_download(self, **kw):
        pass

    def cmd_install(self, **kw):
        # read raw lexical data
        data = []
        for i in ["A.tsv", "B.tsv", "C.tsv", "D.tsv", "E.tsv", "F.tsv"]:
            with open(self.dir.joinpath("raw", i).as_posix(), encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter="\t")
                raw_lexemes = [row for row in reader]
            data.extend(raw_lexemes)

        # add information to the dataset
        with self.cldf as ds:
            # add sources
            ds.add_sources(*self.raw.read_bib())

            # add languages to dataset
            lang_map = {}
            for language in self.languages:
                lid = slug(language['Source_ID'])
                ds.add_language(
                    ID=lid,
                    Name=language['Name'],
                    Glottolog_Name=language['Glottolog_Name'],
                    Glottocode=language['Glottocode'],
                    ISO639P3code=language['ISO639P3code'],
                    Latitude=language['Latitude'],
                    Longitude=language['Longitude'],
                    Family=language['Family'],
                    Location=language['Location'],
                    Source_ID=language['Source_ID'],
                    List_ID=language['List_ID'],
                    List_Name=language['List_Name'],
                    Note=language['Note']
                )
                lang_map[language['Source_ID'].strip()] = lid

            # add concepts
            for concept in self.concepts:
                ds.add_concept(
                    ID=concept['ID'],
                    Name=concept['ENGLISH'],
                    Concepticon_ID=concept['CONCEPTICON_ID'],
                    Concepticon_Gloss=concept['CONCEPTICON_GLOSS'],
                )

            # add lexemes
            for idx, entry in tqdm(enumerate(data), desc='make-cldf'):
                entry.pop('ENGLISH')
                entry.pop('LIST ID')
                glossid = entry.pop('GLOSS ID')

                for lang, value in entry.items():
                    lang = lang.strip()

                    for form in split_text(value, separators='/', strip=True):

                        # strip brackets
                        form = strip_brackets(form, brackets={'(':')'})

                        # skip over empty forms
                        if form in ["-", ""]:
                            continue

                        # add form
                        for row in ds.add_lexemes(
                            Language_ID=lang_map[lang],
                            Parameter_ID=glossid,
                            Value=form,
                            Source=['Backstrom1992']):
                            pass
