# Attempt 043 — source and response manifest

Base `92f341e169f7e81775a7f006ae39757303a8e88f`; isolated uncommitted branch `codex/gpt6-sol-luna-eval-20260926`. Ignored `benchmarks/results/gpt6-sol-luna-20260926/runtime/` holds complete direct-provider raw envelopes, usage ledger and all diagnostics. This tracked manifest contains hashes, sizes and IDs, no secret values. OpenAI and Gemini envelopes were retained before parsing. See [Attempt 043](../attempts/043-gpt6-luna-detector-runtime-qualification.md) for guarded stages and verdict.

## Source and tooling

| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `modules/common/openai_crop_vision.py` | `877a46b2b5a17a94209886380c6907ac59073b308a10252b69b9003280a1821b` | 9965 |
| `modules/common/google_client.py` | `174e4469436f26452a8d0712af32968ddfa730a04a726bf34d272d970aadd721` | 6099 |
| `modules/extract/crop_illustrations_guided_v1/main.py` | `d5235ecfbc639e8850c4d227be1c01201ac49f886eba3dcd7d637de2f24b4dac` | 225879 |
| `modules/extract/crop_illustrations_guided_v1/module.yaml` | `22fdc7a8995807d0bc72e0244bd03774e14da216cdc29d796e8b5939fc16f1c0` | 17728 |
| `configs/recipes/story-236-gpt6-luna-detector-runtime-validate.yaml` | `62f954f3877e8bc9247d43edf2a2e57c4d353cfbac988751a357cb909cab1704` | 2216 |
| `configs/recipes/story-236-gemini-crop-runtime-validate.yaml` | `83ee630d5ef259b34339ba59509120c4b508155e72e4f3570d04f344b551afbf` | 2130 |
| `configs/recipes/story-236-gpt6-luna-detector-runtime-validate-caption2048.yaml` | `acf6f71d6130c8bc42ed5579041608aac0739eeb25a5116290aa7faec4616d63` | 2217 |
| `configs/recipes/story-236-gemini-crop-runtime-validate-caption2048.yaml` | `6a94e2a503942a7d960ef92f15ec7c58c2ed5a876c95b442760a858912385d07` | 2131 |
| `output/fixtures/gpt6-luna-crop-runtime-20260926/pages_html.jsonl` | `6efe638179e1ec636549ff3a918e681383f845a95d9aab72ec447b676fa5346b` | 2849 |
| `input/onward-to-the-unknown-images/Image000.jpg` | `becf83c67a8c5659428be07f8559b798b300480e52df4c969b52be709ff107c9` | 6333897 |
| `input/onward-to-the-unknown-images/Image011.jpg` | `2246934ed6dc9fcc2531ca4fa2d0913bbd5fca99eeea40093ce9de623f819265` | 1122475 |
| `input/onward-to-the-unknown-images/Image121.jpg` | `0a0d55a66832d0b4edc8b079b5f75a9cbbdd0167cb70d47432d43ceac754bfad` | 7333652 |
| `input/onward-to-the-unknown-images/Image124.jpg` | `9822f1dc526c91fce4dd2d6d390503ff4d5414355eb1e29bc5b60a6240b63d63` | 1316060 |
| `benchmarks/results/gpt6-sol-luna-20260926/runtime/receipts.json` | `fb80035c4dab21702bd9e0c63d06f255d5f62eac52eefffa2a7d391cb63a5ae8` | 24607 |
| `benchmarks/results/gpt6-sol-luna-20260926/runtime/cost-summary.json` | `20f57a3bd0f1ae3c024a2df405c4aa9246993ac6c78acc988a907cdc98801748` | 842 |

## Owner driver manifests

| Run ID | SHA-256 of `illustration_manifest.jsonl` | Bytes | Crops |
| --- | --- | ---: | ---: |
| `story236-gpt6-luna-r1` | `b239c6283fd31ac91f31c3c28572b663e14bb155455096e17e162a337bbdff5a` | 7913 | 7 |
| `story236-gemini-r1` | `2f54a1265000e89f3da9bf4a6dbb4edd5f2b087087ba49387927af20287e273c` | 9666 | 9 |
| `story236-gemini-coordinate-fixed-r2` | `5eed720754a065b20b5452912dacd6c709e810fdb34a6a1676c80774187ab274` | 9829 | 9 |
| `story236-gpt6-luna-layout-parity-r3` | `4345a41da32edf8c3ca443b820eabdaa45ca70005186afe6a828cab095be5c25` | 8322 | 7 |
| `story236-gemini-layout-parity-r4` | `9d40b2fad77d875fe70a0ce1001e8ed4232b52ef46c98525909b7564a52a8463` | 7950 | 8 |
| `story236-gpt6-luna-caption2048-r5` | `79503495ae196bb2dd7114160798da10384bdae18908626812d5989eefeec7a3` | 7511 | 7 |
| `story236-gemini-caption2048-r6` | `503b82bd42a27c7b3554a3e175321827623cd4affd591c18cad7355335c3ab5b` | 9662 | 9 |

Every run above has a resolved `output/runs/RUN_ID/snapshots/recipe.yaml`, plan snapshot, pipeline state, final crop manifest and image files under the ignored owner output directory. The raw source inspection overlay is `output/inspection/story236-page12-raw-vs-final.jpg` (red = raw Luna box, blue = final crop, coincident).

## Paid raw responses

| Arm | Count | Cost USD | Served identity and finishes |
| --- | ---: | ---: | --- |
| `raw-gemini-candidate` | 3 | 0.0054975 | gemini-3-flash-preview; {"['MAX_TOKENS']": 3} |
| `raw-gemini-candidate-caption2048` | 3 | 0.0111015 | gemini-3-flash-preview; {"['MAX_TOKENS']": 1, "['STOP']": 2} |
| `raw-gemini-candidate-parity` | 3 | 0.0054975 | gemini-3-flash-preview; {"['MAX_TOKENS']": 3} |
| `raw-gemini-control` | 6 | 0.0361545 | gemini-3-flash-preview; {"['MAX_TOKENS']": 3, "['STOP']": 3} |
| `raw-gemini-control-caption2048` | 6 | 0.0436725 | gemini-3-flash-preview; {"['STOP']": 6} |
| `raw-gemini-control-fixed` | 6 | 0.0342495 | gemini-3-flash-preview; {"['MAX_TOKENS']": 3, "['STOP']": 3} |
| `raw-gemini-control-parity` | 6 | 0.0396045 | gemini-3-flash-preview; {"['STOP']": 3, "['MAX_TOKENS']": 3} |
| `raw-openai-candidate` | 3 | 0.002745025 | gpt-6-luna; {'completed': 3} |
| `raw-openai-candidate-caption2048` | 3 | 0.00128703 | gpt-6-luna; {'completed': 3} |
| `raw-openai-candidate-parity` | 3 | 0.00127053 | gpt-6-luna; {'completed': 3} |

**Total:** 42 unique IDs, Attempt 043 `$0.181080085`, whole campaign `$0.382724960/$3.00`. The machine-readable row manifest `benchmarks/results/gpt6-sol-luna-20260926/runtime/receipts.json` records for **every** envelope its relative path, SHA-256 filename, byte size, exact served model, response ID, terminal status, token counts and priced cost. The adjacent `cost-summary.json` sums all rows by arm and provider. Distinct OpenAI cache-write tokens are priced separately from ordinary input; Gemini output includes thought tokens.

## Individual raw-envelope identities

| Arm | SHA-256 filename | Bytes | Provider response ID | Terminal status |
| --- | --- | ---: | --- | --- |
| `raw-gemini-candidate` | `11d7a7cb814bcd549f6194fa435137fa21d477771dcd692697b5b69cf0e3b282` | 3763 | `qGS4av-SFI-cz7IP4sjlsAQ` | `['MAX_TOKENS']` |
| `raw-gemini-candidate` | `989c26f6bf77fd8fe97c039796823e9d931a53499921494466ada4e54424f219` | 3374 | `w2S4arOmDKOO6dkPkfSSuAo` | `['MAX_TOKENS']` |
| `raw-gemini-candidate` | `d03aedb7a51de9aca2984c73d89a9190cb13f146e520c80ce2f222c242c4cfe6` | 3192 | `tmS4arTCNMn4qtsP1tLWwQc` | `['MAX_TOKENS']` |
| `raw-gemini-candidate-caption2048` | `6a50f552a70efbc4a318d0f09cc219ae6de5418270d962816eac33ae1bd3235f` | 10455 | `q2i4apr6Gtz4qtsPzfu20AQ` | `['MAX_TOKENS']` |
| `raw-gemini-candidate-caption2048` | `6da2e9892d95c482ff8d2099baecb6d1dee893e2e46c8f69928afd02de4aa74d` | 3416 | `xWi4au2KF-nqz7IPwKnBwQo` | `['STOP']` |
| `raw-gemini-candidate-caption2048` | `6ee89fbc8aa3b206f9120db9c35a8ff470a9bb033e19a37d6bb1788d8d886e67` | 3565 | `1Gi4avDpIKj6qtsPjYyl-Aw` | `['STOP']` |
| `raw-gemini-candidate-parity` | `1235f10fe689e3cb2eaecdc08c2b29fdfdea4846f231c9850fd285bb05416f86` | 3792 | `A2e4aqPeJOXMqtsP-JK8qAU` | `['MAX_TOKENS']` |
| `raw-gemini-candidate-parity` | `45968fffda2ad7fa7ba265e990701520d7d17768c76eb55536547f9b93e3fa22` | 3023 | `FWe4ao7bGI-cz7IPhMjlsAQ` | `['MAX_TOKENS']` |
| `raw-gemini-candidate-parity` | `c5e08a8b98ca5b7011d4ed2f4a94da666d0cd1f0a4c1ef45f1fcd4480b6eabb3` | 3373 | `I2e4aoHkOLKQ6dkP8OvfYA` | `['MAX_TOKENS']` |
| `raw-gemini-control` | `2d5e42cee7b19223b2e3d96b35b06434ec140814b955cb785c9e2f523dc592af` | 3023 | `DmW4aqPLL73oz7IP0JChsAE` | `['MAX_TOKENS']` |
| `raw-gemini-control` | `3943d445f55a24c5459466edb2f7165fb83c9d7449e26fa9005d1e2a4364ed43` | 6430 | `A2W4asuIKrG2qtsPpsOgiQo` | `['STOP']` |
| `raw-gemini-control` | `4dd1bb5483e18a9d24de833f4f16806bf6f8b7035bd6386c8f239a327c440026` | 21006 | `4mS4arHpLv3_qtsPqq7s6Qs` | `['STOP']` |
| `raw-gemini-control` | `735a3bc44c3c8f8456de364fc625009d0a9fa206b6c47ace169bded2af5ef076` | 3485 | `_mS4auzoLu6eqtsP_6DwuQc` | `['MAX_TOKENS']` |
| `raw-gemini-control` | `bcf5438e42e87de79a96ca34345c9072e4266cf5cad2f8aae04cc6674b3a5161` | 3495 | `IGW4av3hONyRmtkP38Ch8As` | `['MAX_TOKENS']` |
| `raw-gemini-control` | `ddabb8cbfd174b73d3dc39d419182487d5651e52a012653ba78216450e4856cb` | 8676 | `FWW4aveGN8bjz7IPlY2DuQM` | `['STOP']` |
| `raw-gemini-control-caption2048` | `06a368aada85001129f53c746f4d771e3bf1d74599ddbc02b7ef71b22e10144c` | 8722 | `HWm4aqrSMb39qtsP0J6N0A0` | `['STOP']` |
| `raw-gemini-control-caption2048` | `18d42f8befa74f7a34fc8736d51a0272d04542d93d2789dadaef43d2f1098d49` | 3415 | `OWm4avzAH6Xgz7IP6bndYQ` | `['STOP']` |
| `raw-gemini-control-caption2048` | `4490b7626e1fe62adc07658c3bdc8befcea3e65c86b5a1ec81139421e240d064` | 25546 | `_Wi4auvYK_ug6dkP7ZW9KQ` | `['STOP']` |
| `raw-gemini-control-caption2048` | `788cca60201639d72aa08f83806976377d17be55b745e4af11123406809ee1b8` | 9771 | `K2m4arz2K-ydz7IP8tfImQE` | `['STOP']` |
| `raw-gemini-control-caption2048` | `9439def0e570ff07971dda952b680b3c247a783bb038a8f2a009efc3897f0a1f` | 4005 | `R2m4arOzGIr8qtsPn9ec8Q0` | `['STOP']` |
| `raw-gemini-control-caption2048` | `e08d4fb0acc3c9e2c20923f220f9a9b41bcb15411e24113a8ac3ee8c5a0e2889` | 3828 | `Qmm4auzZHpigz7IP8LeJgA0` | `['STOP']` |
| `raw-gemini-control-fixed` | `331ecb8b7240d0e66f49dcf2e2c8bcc0da3255e677fceb72de619f89aeb3dc90` | 3624 | `wmW4arbRI_ug6dkP7ZW9KQ` | `['MAX_TOKENS']` |
| `raw-gemini-control-fixed` | `44bbd8f091d8a655671a129660d4d5ea3b85f943859560a7f048e620decc69cd` | 6430 | `x2W4atDBCvqNmtkP2tqdsAM` | `['STOP']` |
| `raw-gemini-control-fixed` | `4b02082a376386e9280211ac3f3d317a7446c5931b9b960e79edcca009da1d9b` | 25547 | `oWW4asKOI5Toz7IPt_Sx6A8` | `['STOP']` |
| `raw-gemini-control-fixed` | `776a0f16409b117ca95a1f3985715095aa123b1c638cb803469c95b7930a5e44` | 3374 | `3WW4avytNKHUz7IPofiN-AU` | `['MAX_TOKENS']` |
| `raw-gemini-control-fixed` | `b157bddb2f5a3740ed31c73209c62f81fc3c26b88a31aa9f3a44630d1256d44f` | 3828 | `2GW4apyHFbjiqtsPm6qM8Ag` | `['STOP']` |
| `raw-gemini-control-fixed` | `eae6823b0b38540886f6490af645a332f9b178ca3b2903f82f91687cd312c1ad` | 3023 | `0mW4aqqEIYvzz7IP2a25kQM` | `['MAX_TOKENS']` |
| `raw-gemini-control-parity` | `611a4687444974440f455ba6526db9364266a0236e7ffdf2ce63517d42640bb1` | 9771 | `cGe4aqLTL5KhqtsPq8HRiQk` | `['STOP']` |
| `raw-gemini-control-parity` | `77a64c55d4478164bc3a2b054d6cb086d3d896a3d3a2157d4081734371bcb2dd` | 3374 | `kGe4apW_Mpv-qtsPq_2YoAw` | `['MAX_TOKENS']` |
| `raw-gemini-control-parity` | `9f272efaee5de0e87fcc2230b98753bdc5f61e9f8ff681ad3be9d75109680684` | 3023 | `f2e4apCYA_-Cz7IP39aEkA0` | `['MAX_TOKENS']` |
| `raw-gemini-control-parity` | `ac51b6387a7a12ce9cbe30312436809aabd2f5d9ab286c145c15cc9479b6563e` | 3728 | `aGe4au7IOK6Bz7IPr-LB4Q0` | `['MAX_TOKENS']` |
| `raw-gemini-control-parity` | `cfc7d6b28e3896dc68fb478e310fef0f3274e19ee982cd163c267e6f2f757731` | 21006 | `UWe4apGiJePrz7IPnLzOoA0` | `['STOP']` |
| `raw-gemini-control-parity` | `e074cd1ea309678bf08de7efc72d603c9fa38919d0849ff26b411a3c474dc68d` | 8675 | `h2e4asrzF7rUz7IPhovEkAM` | `['STOP']` |
| `raw-openai-candidate` | `08a94df0cf2bce45039a15bd629bdbb0aecd4bcfabc4e39d9eecfc44a9c04e18` | 16755 | `resp_030ad517f5a2d3bc016ab8649a255087d0b12da12b485072d6` | `completed` |
| `raw-openai-candidate` | `1c7cbc5b4dbe2573531f9a0a83af70ad23e257eb10a462f5f2a6700b221f78ca` | 6608 | `resp_031e7e3abe8f736b016ab864addccc87d081a44a89e19b1924` | `completed` |
| `raw-openai-candidate` | `d6153b38e8bb08fcafdd0fbf552f0d17e7f4467bae7dee8cf420a91c3733bcec` | 5822 | `resp_0b53bb456cb2911f016ab864bda4e887d0b0644449be59277b` | `completed` |
| `raw-openai-candidate-caption2048` | `3c00b98f62c490fb0d543471e89066d9ecaa838a8ef3daf5ec3d895bf313d9f6` | 7029 | `resp_0ea60fb6c041cfe0016ab868b9cbf087d099d35e58ee7de8d6` | `completed` |
| `raw-openai-candidate-caption2048` | `57415daaf8c74e2eba1ed5eb2c69203a839d2457ae3ce96adfef9e6844ac6c6c` | 11827 | `resp_0f226131c8aa1076016ab868a0bb3487d0ae96340a272bc28f` | `completed` |
| `raw-openai-candidate-caption2048` | `748a23be8248aafa5fe237210ae7d93740355cdb6ed9fa9417401ff4552a18a9` | 6639 | `resp_088feee6e606ab53016ab868cdd8d887d08a994cf391125114` | `completed` |
| `raw-openai-candidate-parity` | `1bbafbea96199b4d6b6a996d4af7ca227ad5f86b8b5d1f7f9b73b0ef1a09395b` | 6126 | `resp_035f579e3c6135b8016ab8671dfd9887d08a1fef8bef063575` | `completed` |
| `raw-openai-candidate-parity` | `a059c27ef759f7e823c4814eda6044328da6d184fd4841c95c6b50bdd3b23859` | 7185 | `resp_0c1118bde4365b2c016ab8670c7e6087d098707125742cb791` | `completed` |
| `raw-openai-candidate-parity` | `a35694562368bf8e31ad0a8daa63aa9c16ecf5f07dc00090828a92e1bf824554` | 12232 | `resp_0fa7a2c8f0bc7dc5016ab866f8f80487d0ae7755ffca629d89` | `completed` |

No raw response was modified after retention. Diagnostic failures, including Gemini `MAX_TOKENS`, remain present and billed, not scored as normal captions.
