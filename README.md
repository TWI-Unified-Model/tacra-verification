# tacra-verification

The formal models and the hardware measurements behind the TWI SIG's work on TACRA
([draft-novak-rats-tacra](https://github.com/TheBankster/rats-tacra)) and its EST profile
([draft-novak-lamps-tacra-est](https://github.com/TheBankster/lamps-tacra-est)): what the binding
of Credential Keys to Evidence guarantees and under which assumptions, and what a confidential VM
costs per fresh report. The code they verify and measure is the group's EST server,
[TWI-Unified-Model/globalsign-est](https://github.com/TWI-Unified-Model/globalsign-est) (master
623c197 of 13 October 2026), and the platform back-ends of
[TWI-Unified-Model/tacra](https://github.com/TWI-Unified-Model/tacra). This repository holds no
server code: it is the place the drafts and the server point to for the models, the numbers and
the runs they come from.

| Topic | What it answers | Where |
|---|---|---|
| Formal model | which bindings stop which substitution by the untrusted conduit, and what each guarantee rests on: twenty-four ProVerif models, 62 recorded verdicts | [formal/README.md](formal/README.md) |
| Report rate | how long a confidential VM takes to produce fresh Evidence on AWS, Azure and Google Cloud, SEV-SNP and TDX, one request at a time | [docs/measurements/report-rate.md](docs/measurements/report-rate.md) |
| Handle lifetime | why a Freshness Handle's lifetime has a floor: the GHCB rate limit, the Linux guest driver's retry, every tenth report on Google Cloud SEV-SNP waiting 10.2 s | [docs/measurements/handle-lifetime.md](docs/measurements/handle-lifetime.md) |
| The runs | the nine runs of 5 and 13 October 2026, byte for byte as copied from the machines, never edited | [docs/measurements/evidence/](docs/measurements/evidence/) |
| Repeating them | the probe and the three cloud scripts; each creates one VM, measures, copies the results here and deletes the VM | [scripts/measure/](scripts/measure/) |

## Repository structure

```
.
├── formal/                      # the ProVerif models, their generator and the tool's output
│   ├── gen.py                   # writes the twenty-four models from one template
│   ├── target_first.py          # the same models with the Target before the identifier
│   ├── check_results.py         # runs ProVerif and compares the verdicts with the recorded run
│   ├── *.pv                     # the models, as gen.py writes them
│   └── results/                 # ProVerif 2.05 output, unedited, of 26 and 30 September and 13 October 2026
├── docs/measurements/
│   ├── report-rate.md           # the report-rate measurement and its tables
│   ├── handle-lifetime.md       # the Handle-lifetime floor and where it comes from
│   ├── summary.json             # every figure of the tables, recomputed from evidence/ (checked by CI)
│   └── evidence/<run>/          # the raw records of each run: per-call timings, dmesg, kernel, instance, VM deleted
└── scripts/measure/
    ├── report_burst.py          # the probe: N back-to-back attestation requests in a guest, timed
    ├── burst_stats.py           # the statistics of a run, the source of every number quoted
    ├── summarize_runs.py        # recomputes summary.json from evidence/
    ├── aws-report-rate.sh, azure-report-rate.sh, gcp-report-rate.sh   # one VM each, measure, copy, delete
    └── lib-gcloud.sh
```

## Checks

`make check` runs what CI runs on every push ([.github/workflows/check.yml](.github/workflows/check.yml)):

- `formal/gen.py` writes the models byte for byte as committed;
- ProVerif 2.05 on the twenty-four models gives the recorded 62 verdicts, model by model
  (`formal/check_results.py` against `formal/results/proverif-20261013T142417Z-rerun.txt`);
- `scripts/measure/summarize_runs.py --check`: `docs/measurements/summary.json` is what
  `burst_stats.py` computes from the runs, so every figure of the tables traces to a file in `evidence/`;
- the three cloud scripts parse (`bash -n`).

CI builds ProVerif 2.05 from the official tarball
(`https://proverif.inria.fr/proverif2.05.tar.gz`, sha256
`4871f53c32ab4a04669a060c4886ba5d9080496963fb980a9a62d2c429ceabc4`) with `./build -nointeract`,
which needs only the `ocaml` package; the twenty-four models take about a second.

## Reproduce

The models (ProVerif 2.05 on PATH, or `PROVERIF=/path/to/proverif`):

    make check
    make proverif          # a new recorded run in formal/results/

The measurements, on a cloud account of your own (each script creates one VM, runs the probe in
it, copies the results into `docs/measurements/evidence/` and deletes the VM; see
[report-rate.md](docs/measurements/report-rate.md), "Repeating the measurement"):

    scripts/measure/aws-report-rate.sh us-east-2 us-east-2a
    scripts/measure/azure-report-rate.sh westeurope
    TEE=sev-snp scripts/measure/gcp-report-rate.sh us-central1-c
    TEE=tdx scripts/measure/gcp-report-rate.sh us-central1-a
    make summary           # recompute summary.json from the runs

## Provenance

The models, the measurements and the texts were first published in
[nikolaichuk7/tacra-est](https://github.com/nikolaichuk7/tacra-est) under Apache-2.0 and offered
to the TWI SIG as [TWI-Unified-Model/globalsign-est pull request #7](https://github.com/TWI-Unified-Model/globalsign-est/pull/7)
(commit 2e08899, kept by that pull request). This repository is that tree, unchanged, except:

- this README, `LICENSE`, `NOTICE`, `Makefile`, the workflow, `formal/check_results.py`,
  `scripts/measure/summarize_runs.py` and `docs/measurements/summary.json` are new;
- three references in `formal/README.md` and `docs/measurements/handle-lifetime.md` that pointed to
  files of the EST server's repository now link to them at master 623c197
  (`internal/tacra/binding.go`, `internal/tacra/backend.go`, `internal/mockca/attest.go`);
- the licence lines of the three documents say Apache-2.0 instead of that repository's MIT.

`code-rev.txt` in each run names the commit the probe was run from: for the runs of 5 October,
commits of nikolaichuk7/tacra-est; for the runs of 13 October, 4212c338bb01, the commit of pull
request #7's branch before those runs were added to it (its tree is 2e08899 without
`evidence/20261013T*` and the second table of report-rate.md). The evidence files themselves are
never edited; the statistics are recomputed from them.

## Licence

Apache-2.0, as [TWI-Unified-Model/tacra](https://github.com/TWI-Unified-Model/tacra). Copyright
2026 Serhii Nikolaichuk; see `NOTICE`. The files under `formal/results` are the unedited output of
ProVerif, which is not part of this repository.
