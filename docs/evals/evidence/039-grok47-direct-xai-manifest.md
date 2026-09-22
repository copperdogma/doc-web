# Attempt 039 Grok 4.7 Direct xAI Manifest

All files below are ignored public-fixture artifacts under
`benchmarks/results/grok47-20260922/`. They contain no authorization headers or
keys. The response envelopes are retained locally for offline inspection; this
tracked manifest supplies stable hashes, sizes, and regeneration commands.

## Result files

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `full13.json` | 9637442 | `9f83f75a90f263df21dd8b152a1d0b50c03fee2493b028af465bcc6e69b01a01` |
| `image011.json` | 319954 | `78b0201f50d92ccb1a0c149a5009f81c83191b86c48c627d8573086daeac6a5d` |

## Raw envelopes

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `056c845f-d2f7-9188-a457-5457f70e4b92-ba94ba3a08e9.http.json` | 4358 | `ba94ba3a08e9cfc4136aae6589e970277c42aca0644f2c750fbd7b34c6ce7496` |
| `0e044929-3254-971a-86b1-20b21a10f3e0-7436c158b7c6.http.json` | 4227 | `7436c158b7c6a308e81fe077e7c78931ce6df6094d0e3f74b0df4c11abbeec15` |
| `30b0c47b-e68c-93c7-96f2-85bcd522f00a-5b0eb284257d.http.json` | 5702 | `5b0eb284257d84366ca113ec8d859d014cb3f96c1d317c02a5fe553832632cea` |
| `410536f9-3fd7-90e5-aae8-8b6ab08fff6c-8f98b22141ff.http.json` | 7553 | `8f98b22141ff254a5a4d9ec33d28f52789b933b1db54a342f2a885290959b5fb` |
| `410cce93-09b8-91c3-b894-4f2e99c32ed9-0f583a0c9fca.http.json` | 3674 | `0f583a0c9fca3c7c3264c0f6e1966cc31ba263507326f182065808efa494132c` |
| `43f2a5b7-fbcd-9d39-b1ca-c927f041319d-2f2440f5054a.http.json` | 2857 | `2f2440f5054afa797997e8162cc8b30f91523cc178b3fe97cd2be5694d6aa0bb` |
| `591d0101-b747-9d55-ae09-3c7aabe27087-1674049b1422.http.json` | 4872 | `1674049b1422aef94bab4f89da6335cce53e10e2bce09847209aac72f5b785e7` |
| `612cc7b1-89f3-9f18-8567-3f7760b02191-0bc9c9a61808.json` | 7946 | `0bc9c9a618080d4788a30a48985eba5f0a557369662440f0c8e8af7d6bd3647e` |
| `6cd0bd61-e6c6-9fb7-9d94-7bb23025179f-38f4138f7c32.http.json` | 7618 | `38f4138f7c32a27b3edd6b27ec9c8ca27ee7babf6294fc98f9e756778abcde38` |
| `7362fa4a-b1d1-9c32-bf0e-e3edefa9bb36-8eb0229c2a4d.http.json` | 3415 | `8eb0229c2a4de66f35fd62272e9c417e2766e4683abbd305d14cfe1d8d78e7a3` |
| `98a13233-c379-97ad-8de7-effe202040f1-52040bd886a9.http.json` | 3684 | `52040bd886a98443b5926bab7ed0366ff71da659068826a3f88644482c1e4871` |
| `9bef669c-168e-98c9-8058-16d907f027f5-420b1c37da32.http.json` | 6803 | `420b1c37da32bdb921a2cf27819fa336ab43487cefee203b20364f4e111cca2e` |
| `b2ae4039-0acb-9ee9-9873-ab8d41d3fe12-84b3bc1d8113.http.json` | 4469 | `84b3bc1d811394290f2597edcd634f09829c26e60b89e3cc74ca93998775ebbd` |
| `bfa3fdd3-cf26-9a1e-be25-89a4a634fd9c-f59511896e32.http.json` | 4462 | `f59511896e32f34db6ca9517b0d3eb55525c40ef2ba60e561b21ba6f3e5d5d46` |
| `dfaf6574-39fe-938b-85d5-2124fafac087-af8fd487398d.json` | 7397 | `af8fd487398d92e7e5847dbb7e920cb9029859d3061438201649eee955df05b5` |
| `ed93017b-bfbc-9484-b2ef-d8f2fad3ee74-6335050bcae1.http.json` | 5895 | `6335050bcae1858d74a3f101f02e36dbc72eea6019cf1134cce6a94f5f887870` |
| `fb1e66b7-786c-9a9f-a95c-7d1d5644ec23-f1c71c56c22f.http.json` | 2795 | `f1c71c56c22f1f6e3accd26f449ca594a988eabe87008d83b41c24d37612332a` |

No future result may be compared against this campaign until its exact
path/hash is checked.

## Regeneration

Use the command in Attempt 039 from a fresh worktree at its recorded base,
with an approved temporary `XAI_API_KEY`, the exact source hashes below, and
`XAI_GROK_RAW_ENVELOPE_DIR` set to this ignored result directory. The full13
result is intentionally not a cache source for a fresh evaluation.

| Source | Git object SHA-1 at run |
| --- | --- |
| `benchmarks/providers/xai_grok_responses.py` | `205311f2e8d5ec0156e23023c65b93f36f2d0a62` |
| `benchmarks/scripts/grok47_xai_probe.py` | `e6e99310c926391d8ea2974996784dd173aadcb2` |
| `benchmarks/prompts/crop-conservative-count.js` | `37ec722ab4b00c779db1d16660fcd36dfa7719fd` |
| `benchmarks/scorers/image_crop_scorer.py` | `7592c8074ed2cf3d8707aed8863a64836b75bca5` |
| `benchmarks/golden/image-crops.json` | `97a011f8d78661a91d4ce6b00ddda8f4e4821a07` |
| `benchmarks/tasks/image-crop-extraction.yaml` | `cbc10707b50a98de930c49c4c21359be47e4ded1` |
| `benchmarks/tasks/grok47-image011.yaml` | `c453dd7507e75cd266318b066e5a9d4206164e13` |

## Post-run offline capture repair

After the paid calls completed, the native qualification helper was hardened
offline to retain the raw HTTP body before status or JSON handling, matching the
adapter's behavior. This does not alter the run-source snapshot above or any
recorded result. Reversing
`docs/evals/evidence/039-grok47-post-run-capture-repair.patch` against the
candidate source reconstructs the recorded run-source hash. The candidate source
blob is:

| Source | Git object SHA-1 after offline repair |
| --- | --- |
| `benchmarks/scripts/grok47_xai_probe.py` | `83a40320a4186e21bf08517edd5a995f76161c93` |
| `docs/evals/evidence/039-grok47-post-run-capture-repair.patch` | `146aeb6d790bb572d0a3b9164789a6cce4e77380` |
