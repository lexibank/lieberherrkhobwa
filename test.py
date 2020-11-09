def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    assert len(list(cldf_dataset["FormTable"])) == 2144
    assert any(f["Form"] == "kʰin-ʨʰɔk" for f in cldf_dataset["FormTable"])


def test_parameters(cldf_dataset):
    assert len(list(cldf_dataset["ParameterTable"])) == 100


def test_languages(cldf_dataset):
    assert len(list(cldf_dataset["LanguageTable"])) == 22


def test_cognates(cldf_dataset):
    assert len(list(cldf_dataset["CognateTable"])) == 2144
    assert any(f["Form"] == "ʨʰak-ba" for f in cldf_dataset["CognateTable"])
