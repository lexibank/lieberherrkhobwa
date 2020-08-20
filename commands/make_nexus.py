"""
Write SplitsTree and BEAST nexus files for the lieberherrkhobwa dataset.
"""

import lexibank_lieberherrkhobwa
import lingpy
from lingpy.convert.strings import write_nexus


OUT_PATH = "out/"


def run(args):
    ds = lexibank_lieberherrkhobwa.Dataset(args)
    wl = lingpy.Wordlist.from_cldf(
        ds.cldf_dir / "cldf-metadata.json", col="language_id", row="parameter_id"
    )

    wl.add_entries("cogid", "cognacy", lambda x: int(x), override=False)

    write_nexus(wl, mode="SPLITSTREE", filename=OUT_PATH + "lieberherrkhobwa-splitstree.nex")
    write_nexus(wl, mode="BEAST", filename=OUT_PATH + "lieberherrkhobwa-beast.nex")
