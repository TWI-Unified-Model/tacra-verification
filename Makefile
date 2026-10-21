# The checks CI runs on every push; `make check` runs them here. ProVerif 2.05 is expected on PATH
# or in PROVERIF (built from https://proverif.inria.fr/proverif2.05.tar.gz with ./build -nointeract).
PROVERIF ?= proverif

.PHONY: check gen-check proverif-check summary-check sh-check proverif summary

check: gen-check proverif-check summary-check sh-check

gen-check:
	cd formal && python3 gen.py && git diff --exit-code -- '*.pv'

proverif-check:
	python3 formal/check_results.py --proverif $(PROVERIF)

summary-check:
	python3 scripts/measure/summarize_runs.py --check

sh-check:
	for f in scripts/measure/*.sh; do bash -n "$$f" || exit 1; done

# A new recorded run of the 24 models, with the header lines the recorded runs carry.
proverif:
	python3 formal/check_results.py --proverif $(PROVERIF) --out formal/results/proverif-$$(date -u +%Y%m%dT%H%M%SZ).txt

summary:
	python3 scripts/measure/summarize_runs.py
