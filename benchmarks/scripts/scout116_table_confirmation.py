"""Freeze an unseen source-authored table before its matched confirmation pair."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from scout116_doc_web import E, RAW, ROOT, CANDIDATE, astra_request, digest, write

fixture = E / "heldout-table"
source = E / "heldout-table.source.json"
write(source, {
    "title":"Independent ferry inventory",
    "font":"Courier",
    "widths":[150,118,101,135],
    "rows":[
        [{"text":x,"header":True} for x in ["Rack","Seal","Count","Inspector"]],
        [{"text":"Port","rowspan":2},{"text":"B8-S5"},{"text":"0"},{"text":"reread"}],
        [{"text":"B6-S3"},{"text":""},{"text":"Re-read"}],
        [{"text":"Starboard"},{"text":"Q2-Z7"},{"text":"-"},{"text":"pre load"}],
        [{"text":"Reserve"},{"text":"q2-z7"},{"text":"+1"},{"text":"pre-load"}],
        [{"text":"Keep marked spaces and empty cells.","colspan":4}],
    ],
})
subprocess.run([sys.executable,"testdata/generate_literal_table_fixtures.py","--source",str(source),"--out",str(fixture)],cwd=ROOT,check=True)
matrix_path=E/"preflight.json"
pre=json.loads(matrix_path.read_text())
if "table-heldout-astra62" in pre["matrix"]:
    raise RuntimeError("Already frozen")
control=astra_request(fixture/"page.png")
candidate={**control,"model":CANDIDATE,"max_output_tokens":32768,"reasoning":{"effort":"high"}}
for label,body in [("astra",control),("astra62",candidate)]:
    name="table-heldout-"+label
    path=RAW/(name+".request.json")
    if path.exists():
        raise RuntimeError("Held-out request exists")
    write(path,body)
    pre["matrix"][name]={
        "lane":"table","model":body["model"],"request_sha256":digest(path),
        "body_path":str(path.relative_to(ROOT)),"independent":True,
        "image_sha256":digest(fixture/"page.png"),
        "golden_sha256":digest(fixture/"golden.html"),
    }
pre["heldout_table_provenance"]={"generator":digest(ROOT/"testdata/generate_literal_table_fixtures.py"),
    "fixture_source":digest(source),"rendered_fixture":digest(fixture/"page.png"),
    "before_extension_matrix_sha256":digest(matrix_path)}
write(matrix_path,pre)
