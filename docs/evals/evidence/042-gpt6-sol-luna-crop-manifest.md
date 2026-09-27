# Attempt 042 raw and result manifest

Base: `92f341e169f7e81775a7f006ae39757303a8e88f`; worktree branch `codex/gpt6-sol-luna-eval-20260926`. All files under `benchmarks/results/gpt6-sol-luna-20260926/` are ignored, local, and regenerable. Raw OpenAI envelopes were saved before parsing with mode 0600 inside mode-0700 `raw/`. The manifest contains no credential values.

## Frozen source and evaluated tooling

| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `benchmarks/providers/openai_responses_model.py` | `3506470ee1eb9c8da8c472f270e3400fd2c6cbd086c6be836a0d974997696240` | 17928 |
| `benchmarks/prompts/crop-conservative-count.js` | `d15c7fd6f20389e5e7b2af9f15dd3697a31c28f47cfea8147c8114fe82f1e8f9` | 1782 |
| `benchmarks/prompts/validate-page-level-crop.js` | `2ccc8c96ef69c14102d7ffd13b5a39715e5cd136b497510b1b2f88243009a5a0` | 2796 |
| `benchmarks/scorers/image_crop_scorer.py` | `7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7` | 10333 |
| `benchmarks/scorers/crop_validation_scorer.py` | `12eb63725523bd00d59ce12b7486db8c9244124a0c57bb68cae8b8e9e7d288fb` | 4546 |
| `benchmarks/golden/image-crops.json` | `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90` | 7783 |
| `benchmarks/golden/crop-page-level-deletion-gate.json` | `4bcba8f4ab8a742608e7cfc1438464a71cf56aa4cd9cbe9e0a67e4a410ac18a5` | 4476 |
| `benchmarks/tasks/gpt6-detector-gemini-control-20260926.yaml` | `2eee40b3ebb3838dd9e76ed9005d5c511b835d8247249e92878bc9f13759b59b` | 2603 |
| `benchmarks/tasks/gpt6-luna-detector-full-20260926.yaml` | `d9338d687454926159da20f13d9027748e6990d816fd6bb558a1c55ad560ab77` | 2755 |
| `benchmarks/tasks/gpt6-luna-detector-screen-20260926.yaml` | `0bda20a711b02ce68e0273dc69950bd9d1af12f91e7a7187589c1dedcdede2a7` | 703 |
| `benchmarks/tasks/gpt6-luna-page-screen-20260926.yaml` | `fc41b0bb2cffe1dd81fb14d31309e4d50b74d2ecb986047f8cc6d90f483053e8` | 772 |
| `benchmarks/tasks/gpt6-sol-detector-full-20260926.yaml` | `ff7571e941523efe0f0e48fcd1428476e355eee50d1c41dc49e5d2a1b92ca145` | 2752 |
| `benchmarks/tasks/gpt6-sol-detector-screen-20260926.yaml` | `c5dd5f793925e7b8a1276eb837773160a820c07c8c44869a39bd4ada9f0ddec8` | 700 |
| `benchmarks/tasks/gpt6-sol-page-screen-20260926.yaml` | `442c79a76e57b631c1a222f55982fc36d3fbc58f8998707b55dc937fec790e39` | 769 |

## Promptfoo results

| Stage | SHA-256 | Bytes | Rows | Raw envelopes |
| --- | --- | ---: | ---: | ---: |
| `benchmarks/results/gpt6-sol-luna-20260926/sol-detector-screen.json` | `a5f0935333db4cf229ab6cb26c1c388952b5b6a8185f4d452bcd849c5afe847d` | 320033 | 1 | 1 |
| `benchmarks/results/gpt6-sol-luna-20260926/sol-page-screen.json` | `1b3297e2fb346c70bee6fdfd847514fda66499d9c7d766c8f8f4dd9818c44f19` | 8509160 | 1 | 1 |
| `benchmarks/results/gpt6-sol-luna-20260926/luna-detector-screen.json` | `aaa8ad478aed64216bfbc3b21c294995dc257dd5510a8e9e9ff1da38832d6e03` | 320065 | 1 | 1 |
| `benchmarks/results/gpt6-sol-luna-20260926/luna-page-screen.json` | `66cef91e91e81f15d33b5de68c8914e226d0080e9122d7ed0f2f1d16eb12bbed` | 8509366 | 1 | 1 |
| `benchmarks/results/gpt6-sol-luna-20260926/sol-detector-full.json` | `4a6037ad0bded46e2c8d09e2bfc540175a0f746cd2f4796234564ed05766d9ce` | 9624159 | 13 | 13 |
| `benchmarks/results/gpt6-sol-luna-20260926/luna-detector-full.json` | `690e36ac078e31383f5de8154c3a6755a7b153f8bc8cf7a08ff5babcb38f5769` | 9624422 | 13 | 13 |
| `benchmarks/results/gpt6-sol-luna-20260926/gemini-detector-full.json` | `f586edc6e157f8ca5c036e24ea463f49337ecce947ea0c626b0c1ba938401931` | 9680746 | 13 | 0 |

## Complete direct Responses raw envelopes

| Stage | SHA-256 (filename) | Bytes |
| --- | --- | ---: |
| luna-detector-full | `0a036b5b5a151b925afe32fe56dafdbe781e0329a5590ab809adf9ab96132f06` | 4814 |
| luna-detector-full | `0c424aea7f2fd39fe1486f1f3bc7ad83248dfc40fcfd6d00d65a4d33100c51b1` | 4902 |
| luna-detector-full | `3232238158fa8552ea2edc53fc49942beeb25291225cae2c04b815cbb272ddc4` | 5551 |
| luna-detector-full | `509c4fd4c3aa0ffb0b36dad1dc1690d828546b1238abbbc73211fc53a04aaeff` | 5746 |
| luna-detector-full | `5ba50e9849f5e1545e2e2a8a5a4a835e8dded69cdb53e28aafc11d17e7afbc6f` | 4809 |
| luna-detector-full | `6515bf4f299bc82a52a289152e0beb5b1f6eadc3ed1c2f7eb113989cb49dfa20` | 5073 |
| luna-detector-full | `68b17095177424a7273ad0ecf5e588471b7e1c8a63d40daa8f895c3fc117c92a` | 4992 |
| luna-detector-full | `6e461a2d3033bb82e62e5d6778aaa17dfe32bba295142af9b0b4a0b504707abe` | 5086 |
| luna-detector-full | `79140aff5dd2d0a525b278efc9e604d1d72094a593db5546eaaf1b14e8f8e8cb` | 5002 |
| luna-detector-full | `9101b05eff3d50fdb41b6ce93b2e2fe13ac9da2db2421f7b9c46a9291ce946b3` | 4772 |
| luna-detector-full | `ab22383e279c98ee69f112b57033059d597e934d1322969f2bbbd1af3143b31e` | 5160 |
| luna-detector-full | `ec7512f3e177bccfa081497404ac557847b3087d355ee9b445cee28b45383d13` | 4967 |
| luna-detector-full | `f00aae5b71298111d649e3cc29ef86253b6b32359161a2e38c8977d941aebfdb` | 5145 |
| luna-detector-screen | `799790481725bb55a346e105a123c448df5642f33208358e42e1e2c115fa89c8` | 5632 |
| luna-native-detector | `19217d2b286ae649907e93fc02465f91b5521faa0caa3788f98ae89cf71a5c86` | 7420 |
| luna-native-page | `20bceabc05b803692b9ffe0a89284bd827ca37932f6227b22d9f03bb09015c9c` | 2904 |
| luna-page-screen | `a3a0d5c6b38471277b0689d0b3a7b82ae69326da5ea615373af908be4f6f5be7` | 2976 |
| sol-detector-full | `078fe4588acbb0e4615a297d475bc51561c246e7cf6d6100c62843f386782a28` | 3186 |
| sol-detector-full | `07af022dc139cdbca64c04769c00bdfc100fd15248e559195631369e10b6b558` | 3289 |
| sol-detector-full | `0d7d081ea43f3ff3f83f5d2c3e8dc658dae8bf1d502a3dc72afab8eb74375ccd` | 4942 |
| sol-detector-full | `2dc061dcd30f1bd41b10bfa8c8ed449d7a49d243fb86734d7620717b5b1012da` | 3267 |
| sol-detector-full | `4160a6411fb8a19cee5a8290e2e5d050f56fc20018e382ca8287510368e608be` | 3169 |
| sol-detector-full | `72b451cf60efa62299bea1a676559786a4424ef7e82d7197fb306ae8fd4a6d61` | 4688 |
| sol-detector-full | `74a7fccc81eb39fe952d70f0137a0f3d99bbdd869903f0c6de567d313a716347` | 5017 |
| sol-detector-full | `89b3f365979e5488dfdd6504a4aecac8cf56dbf5cc49ef4927ee04f3e87389e5` | 5128 |
| sol-detector-full | `9279178dfa1d6c94c4078957b993e1a2e7f6f8e22c053dd85805fc3e9b903eca` | 4900 |
| sol-detector-full | `9d2457717ad1e57eb2e5a2e9c6ddcf75f8e547908c3be3b3ea027f6b78fb255f` | 3407 |
| sol-detector-full | `b5b06c637f813e79412c6b6374d8209d19e4a2bdabda49e8f05e157f13b376a6` | 5367 |
| sol-detector-full | `c89f3de9a77c080f7e808bbf6b12129893ddaa74ce0ce2fcdce39c35712a63f6` | 4846 |
| sol-detector-full | `e15e0a71fde0eedf60b0a9f1f1e70aac378ec6b2538853eab967969aa1120636` | 5000 |
| sol-detector-screen | `2c429e7c233d266b36a246976de5d03f426ccbade2588c6ace604e42fe043c1b` | 5297 |
| sol-native-detector | `d0e41f142d5e2b446fdadd5a1a92febb0a4933f56a472a700d323ea4494cef33` | 4791 |
| sol-native-page | `0eb6ea202c04bd401f1abeaf6f1ebdbd8a0f8821d6dc312c97f4ecbae33c06df` | 2878 |
| sol-page-screen | `2b54327507f8eaca7d503cb964ec2015496d3f7dea94be91b3751b1eea451a24` | 2928 |

Regenerate only via the guarded stage sequence and exact commands in Attempt 042. In particular, the two page-full templates were removed after false-safe screens and must not be run under this attempt.
