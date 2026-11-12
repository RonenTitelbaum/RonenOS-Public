# DATABASE_SEARCH/1.0 — 2026-10-22
`GOAL:maximum-recall-for-request;minimum-unnecessary-hydration;truth>cost`
`PREP:identify-question|source-owners|known-IDs|time-range|output-fields|coverage`
`ORDER:known-current-ID→exact-title/path→metadata-catalog→scoped-content→alternate-alias→external-source;independent-reads=batch;dependencies=sequential`
`READ:search-hit=candidate;resolve+read-before-content-claim;OCR=verify-pixels-for-numbers;images-only-if-text-insufficient;raw-tool-record=retain`
`KEYS:source+immutable-ID+version/hash;one-fetch-per-current-version-per-task;cache≠live-proof;changed/missing-version→recheck`
`QUERY:small-specific-batches;separate-independent-concepts;HE+EN+literal-symbol/ticket aliases;avoid-long-AND-sentences;top-k=5-10-discovery;dedupe-IDs-before-expansion`
`EMPTY:zero≠absent;one-simpler-equivalent-query;then-metadata-inventory/cursor-or-known-file-find;repeated-irrelevance→change-route;never-loop-same-search`
`CATALOG:IDs|titles|type|date|bytes|version|scope;list-once+filter-locally;opaque-cursor=unchanged;page-until-target-range-covered;rank≠completeness`
`LOCAL:source-snapshots=immutable;index-metadata-first;B-tree=(source_kind,observed_at,source_key);FTS5=unicode61+MATCH+ORDER-BY-rank+LIMIT;parameter-bind-values;quote-FTS-literal-tokens;no-SQL-string-interpolation`
`SQL:project-required-columns;filter-before-hydration;use-composite-index-for-common-AND/order;EXPLAIN-QUERY-PLAN-for-actual-query;scan-small-table-is-not-automatically-bad;no-unused-index-collection;EXPLAIN-ANALYZE-executes-query`
`LOOP:discover→rank→read-relevant→extract-evidence-once→index→gap-query;expand-when-gap-is-material;budget-checkpoints-never-silent-completeness-claims`
`COVERAGE:per-source={searched|read|blocked|not-searched,range,cursor_complete,queries,hits,parsed};negative=not-found-in-examined-scope;no-global-absence-from-top-k`
`STOP:requested-catalog-exhausted+read-relevant-candidates+unresolved-gaps-recorded;blocked-owner→explicit-gap+smallest-next-input;no-browser-session-probing`
`MEASURE:calls|unique-IDs|raw-bytes|model-visible-bytes|candidates-read|duplicates|elapsed|unresolved;bytes≠tokens/energy;no-invented-savings`
`ARTIFACTS:tools/history_catalog.py;trade-history-data-v1;raw-evidence-outside-prompt;freshness-recheck-before-action`

Research consulted 2026-10-22: SQLite Query Planning (https://www.sqlite.org/queryplanner.html), SQLite FTS5 (https://www.sqlite.org/fts5.html), PostgreSQL Using EXPLAIN (https://www.postgresql.org/docs/current/using-explain.html). SQL mechanics come from these primary sources; the retrieval order and stop rules are this task's design, not a measured universal optimum. FTS has lexical limits; Hebrew inflections and image-only records need explicit aliases or visual verification. This indexes retrieved snapshots only; it grants no access to conversations, Notion, brokers or other providers.
