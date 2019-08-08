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

    def clean_form(self, item, form):
        if form not in ["–"]:
            return strip_brackets(form)

    def split_forms(self, item, value):
        if value in self.lexemes:
            value = self.lexemes.get(value, value)
        return [self.clean_form(item, form)
            for form in split_text(value, separators='/')]

    def cmd_install(self, **kw):
        data = []
        for i in ["A.tsv", "B.tsv", "C.tsv", "D.tsv", "E.tsv", "F.tsv"]:
            with open(self.dir.joinpath("raw", i).as_posix(), encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter="\t")
                raw_lexemes = [row for row in reader]
            data.extend(raw_lexemes)

        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())

            add_lang = {}
            for language in self.languages:
                langid = slug(language['Source_ID'])
                ds.add_languages(id_factory=lambda x: slug(x['Source_ID']))
                add_lang[language['Source_ID'].strip()] = langid
			
            for concept in self.concepts:
                ds.add_concept(
                    ID=concept['ID'],
                    Name=concept['ENGLISH'],
                    Concepticon_ID=concept['CONCEPTICON_ID'],
                    Concepticon_Gloss=concept['CONCEPTICON_GLOSS'],
                )

            for idx, entry in tqdm(enumerate(data), desc='make-cldf'):
                entry.pop('ENGLISH')
                entry.pop('LIST ID')
                glossid = entry.pop('GLOSS ID')

                for lang, value in entry.items():
                    lang = lang.strip()

                    for row in ds.add_lexemes(
                        Language_ID=add_lang[lang],
                        Parameter_ID=glossid,
                        Value=value,
                        Source=['Backstrom1992']):
                        pass
