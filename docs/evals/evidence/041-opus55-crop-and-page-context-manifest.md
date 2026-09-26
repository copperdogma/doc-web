# Attempt 041 — protected evidence manifest

All raw provider envelopes and Promptfoo result JSON files are owner-approved public-fixture evidence stored under the ignored `benchmarks/results/opus55-20260926/` directory of this isolated worktree. No credential or request headers are retained. The table records SHA-256 and exact byte size; labels identify the regeneration stage.

| Label | SHA-256 | Bytes |
| --- | --- | ---: |
| native-integer-image | `df43c9f3e879b582c6f36a17c355879c7cc6362fc009409f704f29cc23c6eaf1` | 638 |
| adapter-integer-parity | `547eae2b47bde12d1b5d66c527119cedab90b45563c3c1196e5f05da98677592` | 645 |
| native-page-context | `6c2669359f8c692b9b1ef5c9af7d0fd3f8c183c95c1da8e587889abebfc9de33` | 1990 |
| detector-image011.json:Image011 | `6ffdbc1e4431e3e8060c6a147d16e95c99426e3fa32d9e7269e304ca82013ad3` | 727 |
| page-context-122-001.json:page-122-001 | `0fd0149f023127f74355ba67cab7239592163c19020ddb0657fd41d71f7eb695` | 790 |
| detector-full13.json:Image000 | `0505c9e24e19d688b3605496a383897fcd996efec5d859e7c29bea54be84a402` | 815 |
| detector-full13.json:Image001 | `eda714f8e63c4672c41a23ec33ffc4f791cc602e6f39eb69d7bec15c2d630c27` | 687 |
| detector-full13.json:Image003 | `86bb4224ac49d47cd42822b88fb5bb1992c486a4b9203ccbc91a0c18514c1542` | 849 |
| detector-full13.json:Image008 | `a80ed84105ec52f26c7934c1a08670457bd368613472370d754df007d39a3e72` | 805 |
| detector-full13.json:Image011 | `9be9b67ddd483b9623b189cfb3dae2d3ca2058bb60c59d4c6929b72f1f2175c9` | 753 |
| detector-full13.json:Image013 | `24f32421d2efae5d201447280f29c4338a04b201619592922fd742743dd47ced` | 768 |
| detector-full13.json:Image020 | `e4f0fd6fba7e40721d47486c440d830ae93540b3e230a3f63332d77063d33e05` | 927 |
| detector-full13.json:Image021 | `86d243280565dea3a5e068afb5e90915ea0ba70ec5ef6929671d489037069155` | 818 |
| detector-full13.json:Image037 | `417af95a8d66207c736993b97df3bdce810f481466b22434ad71decd5b384288` | 970 |
| detector-full13.json:Image059 | `ae4625b223f535d42e0d91074b0302311eb3d91794e248aaef85814fb4e9e581` | 973 |
| detector-full13.json:Image121 | `11b7165e39b84957e915fafe481b18fe20bb803c39ae20b291dbaf388b473dd7` | 1097 |
| detector-full13.json:Image124 | `d4bb0a4f90a177a579b8fbb64e09bdcd9bc38b620a43d81631cbe180963335fe` | 788 |
| detector-full13.json:Image126 | `24972466474f5122027b74661b18b20cbe0e194ec2d408778be80ebc73e0138e` | 1030 |

## Promptfoo result bundles

| File | SHA-256 | Bytes |
| --- | --- | ---: |
| `detector-image011.json` | `1aa045a2be49e3b7f4fe834462ec8f6869a2c2e57c93cc051f1ee48f45bd1c50` | 319499 |
| `page-context-122-001.json` | `cb08cba960e7c4545863cca53d2243fa74641159e1b1dab993005e2b83e390b5` | 8509385 |
| `detector-full13.json` | `77ddba9e8502ada388848550ed6b098ef52948b0951f8c28ad9199b1951bd236` | 9620758 |

Regenerate with the exact owner-wrapped commands in `docs/evals/attempts/041-opus55-crop-and-page-context.md`. Native probes used the same public generated square image and the adapter `_build_body` with exact Opus 5.5 `medium`, strict schema and 1024 max output tokens. All evidence remains in the isolated worktree; this manifest does not imply commit, push, merge or permanent archival.
