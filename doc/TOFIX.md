# TOFIX

Findings from a code scan on 2026-10-04.

## Medium

- `package.json:3` - declares `kafkajs` at `latest`, but the repo has no JavaScript code that uses it; `package.json`, `package-lock.json` and the `[processor.ijsonlint]` block at `rsconstruct.toml:62-63` are leftovers. Delete them (or add the missing kafkajs demo).
- `go_apps/go.mod:7` - uses `github.com/confluentinc/confluent-kafka-go` v1.9.2, the unmaintained v1 line; migrate `consummer.go`, `producer.go` and `version.go` to `github.com/confluentinc/confluent-kafka-go/v2/kafka`.
- `go_apps/producer.go:17-21` - the error from `Produce` and the remaining-count from `Flush(1000)` are both ignored, so a failed or undelivered message exits silently with status 0; check both (the Python `scripts/producer.py:44-47` already does this).
- `go_apps/consummer.go:22-28` - `Subscribe`'s error is discarded and `ReadMessage` errors are silently dropped inside the loop; log/handle them so a broker problem is visible.
- `rsconstruct.toml:30,34,39` - `ruff`, `mypy` and `shellcheck` all list `config` in `src_dirs`, but `config/` only holds `.lua` files; drop `config` from those three lists (and `shellcheck` should list `scripts` and `go_apps` only).

## Low

- `go_apps/consummer.go` - filename typo; rename to `consumer.go` (the built binary is named after it by `go_apps/build.sh:5`).
- `scripts/topic_delete.py:90-92` - usage examples say `python delete_topic.py`, but the file is `topic_delete.py` (repeated at lines 106-108); likewise `scripts/topic_list.py:87` says `list_topics.py`. Use `sys.argv[0]` or the real names.
- `pyproject.toml:110` - `mypy_path = "src:python:scripts"` names `src` and `python`, which do not exist in this repo; reduce to `scripts`.
- `pyproject.toml:3` - `version = "0.0.0"` disagrees with `config/version.lua:2` (`0, 0, 1`) and the README's 0.0.1; keep them in sync.
- `config/project.lua:3` - `KEYWORDS` include `sqs` and `jms`, which are unrelated to this Kafka-only repo (they read as copied from another demos-mb-* repo); replace with Kafka-relevant terms.
- `scripts/consumer.py:29-43` - the poll loop never calls `consumer.close()`, so Ctrl-C leaves the group without committing/leaving cleanly; wrap in `try/finally: consumer.close()`.
