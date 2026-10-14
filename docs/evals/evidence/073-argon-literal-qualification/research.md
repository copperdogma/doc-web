# Native contract and bounded request admission — checked2026-10-13

General problem: native image-token sizing and serial billing exposure while
preserving source-authority through actual pipeline stages. Reuse provider-native
structured requests, immutable receipts, and existing flock/exclusive guard;
no custom response repair. Models read pixels; independent source reviewer owns
truth and scalar agreement cannot establish it.

[OpenAI vision](https://developers.openai.com/api/docs/guides/images-vision)
documents Astra original-detail32px patches with1.2multiplier; original retains
these2550x3300dimensions, wellbelow65535 and30000patchrejection. Ceil(80*104*1.2)
plus1roundingtoken=9985. Complete nonimage text/schema UTF8byte bound plus4096
framing is counted separately peractualserializedbody; imagebase64 excluded
onlybecause image tokens are calculated independently. No image resizing/PNG
byte-size token inference. Every complete bound must be<=26000 beforedispatch.

[Google token guide](https://ai.google.dev/gemini-api/docs/tokens) documents
768px image tiles at258tokens;2550x3300covers4x5tiles,5160tokens. Complete
system/user/schema text+framing included separately asabove. Actualnativeusage
must remainwithinbound; anyviolation closescampaign. No tools/multiturn/cache
requests. CountTokens is available but no additional provider call is needed
for this conservative bounded panel calculation.

[OpenAI prices](https://developers.openai.com/api/docs/pricing): standardshort
Astra USD10input/1cached/12.5cachewrite/50output perM. OCRreserve usesworstwrite
rate:26000*12.5+8192*50=USD.7346. Source-reader retainsUSD1.50 bound.
[Google prices](https://ai.google.dev/gemini-api/docs/pricing): nativeArgon
USD2input/.1implicitcache/10inclusivevisible+thinkingperM throughNov30;
Dec1 doubles. Reserve26000*2+32768*10=USD.37968. No explicitcacheavailable;
actualimplicitcache and cold-normalized costsreported separately.
[Argon model](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon)
supports images, structuredoutput andlow/medium/highthinking. Selectedmedium
only; samepolicy/schema, no samplingparameters, STOP/exactservedidentity.

Astra180secondtransport timeout retained. Google1200 nonstreaming transport
allowance retained, withseparate180secondperpageacceptance stop. Batch/relative
criteria areapprovednewproposal, not historicalSLA. Queue/account contention
unmeasured. No populationp95, wholebookeconomics or sourceambiguity recoveryclaim.

## Pre-paid renderer reproducibility finding

The first offline driver replay was denied before POST because the author’s
Pillow12.3 PNG encoder and production runtime Pillow10.4 emitted different PNG
bytes for N1. Independent readback found identical RGB pixels, dimensions and
metadata (pixel SHA89cf2572..., ImageChops differenceNone); compressed sizes
were126174/128591. [Pillow PNG documentation](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html)
explains encoder/compression dependencies. Use the same production interpreter
and renderer for final independently authored fixture bytes; preserve rejected
hashes. Do not re-encode driver outputs or weaken frozen native request/image
hashes. Source author owns this pre-paid correction; execution owner never edits
golds. Final renderer identity and full pixel digests belong in the freeze.
