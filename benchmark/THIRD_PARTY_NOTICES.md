# Third-Party Notices

EvoAgentBench is distributed under the Apache License 2.0 except where noted
below. This file records third-party source incorporated into this repository
and external projects required by individual benchmark adapters.

## Incorporated and adapted source

### BrowseComp-Plus

- Upstream: [texttron/BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus)
- Reference revision: `046949032b0328319cc9a02663a759ec601d9402`
- Upstream license: MIT
- Adapted files:
  - `src/domains/information_retrieval/judge.py`
  - `src/utils/browsecomp-plus-tools/setup_data.py`
  - Python files under `src/utils/browsecomp-plus-tools/searcher/`

The EvoAgentBench versions change configuration, local path handling, model
placement, process lifecycle, and evaluator integration.

```text
MIT License

Copyright (c) 2025 texttron

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### ClawWork

- Upstream: [HKUDS/ClawWork](https://github.com/HKUDS/ClawWork)
- Reference revision: `9c73ac05fdb0bffdb23febdd971eb70f44dd46eb`
- Upstream license: MIT
- Adapted file: `src/domains/knowledge_work/evaluate.py`
- Upstream sources:
  - `livebench/work/llm_evaluator.py`
  - `livebench/tools/productivity/file_reading.py`

The EvoAgentBench version changes provider configuration, removes ClawWork
runtime dependencies, and consolidates artifact readers for GDPVal.

```text
MIT License

Copyright (c) 2026 ✨Data Intelligence Lab@HKU✨

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## External projects not vendored here

The following projects are installed or cloned separately. Their source and
benchmark payloads are not redistributed in this repository.

| Project | Version used by this release | License |
| --- | --- | --- |
| [EverOS](https://github.com/EverMind-AI/EverOS) | `v1.2.3` (`48fc9084888bc17100053227284f939a5aca5e91`) | Apache-2.0 |
| [Tevatron](https://github.com/texttron/tevatron) | `dd063104c81a76d6a77c845f667b46b9e5abd625` | Apache-2.0 |
| [LiveCodeBench](https://github.com/LiveCodeBench/LiveCodeBench) | Installed from a separate source checkout | MIT |
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) | Python package `swebench==3.0.0` / tag `v3.0.0` | MIT |

Benchmark datasets, model weights, indexes, and Docker images are not included
in EvoAgentBench. Their upstream terms apply when users download them.
