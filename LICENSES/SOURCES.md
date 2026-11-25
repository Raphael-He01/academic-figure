# Pinned upstream licence and notice audit

Reviewed 2026-11-16 using read-only GitHub API access; no upstream code or installation scripts were run. Public repositories were independently located rather than treating search summaries as a licence. The former local ZIPs remain unavailable, so exact ZIP identity is not certified.

## nature-figure 2.8.0

Repository: https://github.com/Yuan1z0825/nature-skills . The last manifest-path commit on/before 2026-10-26 was `05af1e218e634a8e687c188caee614591065e30c`; its manifest blob `f7c35c7b2819cf7856bc2f816561ecc0c0853888` states version 2.8.0. A non-truncated recursive tree inspection at that commit found root LICENSE (Apache-2.0) and no file named NOTICE or NOTICE.md. Separate licences in nature-downloader and nature-image2ppt do not describe imported components; neither component is bundled here.

- Manifest: https://github.com/Yuan1z0825/nature-skills/blob/05af1e218e634a8e687c188caee614591065e30c/skills/nature-figure/manifest.yaml
- Licence: https://github.com/Yuan1z0825/nature-skills/blob/05af1e218e634a8e687c188caee614591065e30c/LICENSE
- Tree: https://api.github.com/repos/Yuan1z0825/nature-skills/git/trees/05af1e218e634a8e687c188caee614591065e30c?recursive=1

## ARS-Codex 3.23.1

Repository: https://github.com/Imbad0202/academic-research-skills-codex . Annotated tag v3.23.1 (`624817f795650e6528cb44507cffff0a9e13e8ab`) resolves to commit `71528d9349bcdacfbe94111f06d9e2d82215a44d`. Its non-truncated recursive tree includes the ARS NOTICE and CC BY-NC licence, replicated in the root/skill layouts. Unrelated experiment-agent licences are outside our imported scope.

- Tag: https://github.com/Imbad0202/academic-research-skills-codex/releases/tag/v3.23.1
- Notice: https://github.com/Imbad0202/academic-research-skills-codex/blob/71528d9349bcdacfbe94111f06d9e2d82215a44d/skills/academic-research-suite/ars/NOTICE.md
- Governance referenced by the original notice: https://github.com/Imbad0202/academic-research-skills-codex/blob/71528d9349bcdacfbe94111f06d9e2d82215a44d/skills/academic-research-suite/ars/GOVERNANCE.md
- Licence: https://github.com/Imbad0202/academic-research-skills-codex/blob/71528d9349bcdacfbe94111f06d9e2d82215a44d/LICENSE

`ARS-NOTICE.txt` is the unmodified upstream notice (SHA-256 `4f8eb1306c01b419baeff7f66d96ea3bd46076436406954c7eff21fb2e0003f1`); its relative Markdown names refer to the upstream context above, not additional bundled files. `CC-BY-NC-4.0.txt` is the pinned upstream licence including its copyright statement (SHA-256 `b3848009d12a173f549ef98d9ee486e64459e8eb5d9f895bff53782b4aa86d7c`). Notices preserve upstream context; no claim of affiliation or endorsement is made.

These observations close the missing-NOTICE check for the identified public source snapshots. They do not grant commercial rights or verify every historical ZIP byte. Mixed-file scope and modification statements remain in the root third-party notice.

## scholarly-visualization-lab reference snapshot

The user supplied the skill for comparison. SHA-256 of its manifest is `69959f4e4f79c9cb35c16089270537aad555ea82a737e2eb7c6e612324bf734f`. Its entrypoint has SHA-256 `5c7c35ee4d25203b08626e0ce9940a4cba92f524a3a0988068c530e395cef6d5`. These hashes identify the consulted snapshot. Its START_HERE guide discusses forwarding the intact skill and retaining individual project attributions. A rights holder or licence for publicly redistributing its archive or adapted source files could not be established from the supplied materials.

Academic Figure references the V01–V32 identifiers for compatibility and documents data requirements and chart methods in its own words. Its state-field and sample-atlas components use this project's R implementations and simulated data. Upstream frozen results were used locally for comparisons. Keep upstream source code, figures, data, wording and gallery files out of the public bundle unless their individual permissions have been established. See the [scope of reuse](../THIRD_PARTY_NOTICES.md).
