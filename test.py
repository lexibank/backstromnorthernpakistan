def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    assert len(list(cldf_dataset["FormTable"])) == 11343
    assert any(f["Form"] == "bɑdʌn" for f in cldf_dataset["FormTable"])


def test_parameters(cldf_dataset):
    assert len(list(cldf_dataset["ParameterTable"])) == 1233


def test_languages(cldf_dataset):
    assert len(list(cldf_dataset["LanguageTable"])) == 51
