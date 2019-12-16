import csv
from pathlib import Path

import attr
import pylexibank
from clldutils.misc import slug


@attr.s
class CustomLanguage(pylexibank.Language):
    Source_ID = attr.ib(default=None)
    List_ID = attr.ib(default=None)
    List_Name = attr.ib(default=None)
    Location = attr.ib(default=None)
    Note = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    id = "backstromnorthernpakistan"
    dir = Path(__file__).parent
    language_class = CustomLanguage

    form_spec = pylexibank.FormSpec(separators="/")

    def cmd_makecldf(self, args):
        args.writer.add_sources()
        data = []

        languages = args.writer.add_languages(
            id_factory=lambda x: slug(x["Name"], lowercase=False), lookup_factory="Source_ID"
        )

        for conceptlist in self.conceptlists:
            for concept in conceptlist.concepts.values():
                args.writer.add_concept(
                    ID=concept.id, Name=concept.english, Concepticon_ID=concept.concepticon_id
                )

        for i in ["A.tsv", "B.tsv", "C.tsv", "D.tsv", "E.tsv", "F.tsv"]:
            with open(self.dir.joinpath("raw", i).as_posix(), encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter="\t")
                raw_lexemes = [row for row in reader]
            data.extend(raw_lexemes)

        for idx, entry in pylexibank.progressbar(enumerate(data)):
            entry.pop("ENGLISH")
            entry.pop("LIST ID")
            glossid = entry.pop("GLOSS ID")
            for lang, value in entry.items():
                args.writer.add_forms_from_value(
                    Language_ID=languages[lang.strip()],
                    Parameter_ID=glossid,
                    Value=value,
                    Source=["Backstrom1992"],
                )
