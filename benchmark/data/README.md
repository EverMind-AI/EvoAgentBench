# data

Git only tracks the paper-aligned task IDs in `splits/`. Their immutable
source revision, counts, and checksums are recorded in
`splits/manifest.json`.

Benchmark task data and runtime caches are downloaded separately and remain
gitignored:

- `BrowseComp-Plus/` — BrowseComp-Plus corpus and search indexes.
- `livecode/` — LiveCodeBench cache.
- `swebench/data/test-00000-of-00001.parquet` — SWE-Bench Verified task table.
- `swebench-images/` — optional preloaded SWE-Bench Docker image archives.
- `gdpval/Knowledge Work/` — GDPVal reference files and evaluation prompts.
