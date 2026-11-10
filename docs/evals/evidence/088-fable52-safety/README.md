# Attempt088 durable custody

The original run manifest and producer epochs remain unchanged. `custody-index.json` pins the lossless public/synthetic archive parts stored beside this directory and any protected account metadata kept outside Git. The archives were read back member by member and matched against every original file hash. Original expanded files remain in this retained worktree.

To restore, verify the part hashes, concatenate the listed parts in order, then extract at the repository root. Archive members are regular files with repository-relative paths. The protected account packet is required only for the original rejected OpenRouter access-envelope bytes; it contains no API keys or authorization headers. All scored native responses and source/driver data are in the public packet. Do not rerun inference: the campaign ledger is closed.
