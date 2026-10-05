# Reconciliation of pre-existing local work — 2026-10-05

Scope: the four dirty primary-checkout files explicitly reviewed and authorized
by the user. No new inference, provider availability checks, crop score changes,
runtime changes, or model adoption.

## Historical evaluation notes

Retain all eight scheduled August26–September2 metadata-only observations in
Story207 and the registry. Move the misplaced August29 paragraph outside YAML
front matter. The original supplemental report called itself Attempt028, which
now belongs to Ox Alpha; rename it to
`docs/evals/attempts/deepseek-vision-metadata-followthrough-20260826.md` and update
links. These are archived observations, not freshly verified provider claims.

## Dependency lock

The pre-existing uv.lock matched the project's declared base and optional
requirements but lacked its configured exclude-newer policy. The system uv0.6.3
warned that it could not parse the relative duration and must not be used to
validate that policy. A temporary, isolated uv0.12.23 executable reconciled the
lock without --upgrade; all72 package identities/versions remain unchanged.
The current format records exclude-newer-span=P7D. No project environment or
global executable was upgraded.

Decision: track the reconciled lock to reproduce local development resolutions;
package consumers still use pyproject.toml requirements. Keep the existing
seven-day policy. See primary sources:
https://docs.astral.sh/uv/concepts/resolution/ and
https://docs.astral.sh/uv/concepts/projects/sync/ .

## Validation

- uv0.12.23 lock --check --offline passes for the reconciled lock.
- Old/new lock comparison: all72 package name/version pairs unchanged.
- Story207 YAML header and full eval registry parse successfully; status remains Done.
- Historical scheduled records and report links inspected; no new scored attempt.
- methodology-compile and methodology-check pass; staged whitespace check required.
- No product test suite or paid eval is warranted for these documentation and
  resolution-metadata changes; executable code and dependency versions are unchanged.

Preserve the four original local files in an ignored backup before synchronizing
the primary checkout to the landed commit. No learning candidate: this was a
bounded reconciliation, and existing close-out rules already cover its safeguards.
