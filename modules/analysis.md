# DATA_ANALYSIS/1.1 — 2026-10-22
`PRECONDITION:apply-DATABASE_SEARCH/1.0-before-broad-retrieval;load-that-domain-sequentially-if-not-in-current-chat`
`CONTRACT:goal|unit-of-analysis|population|period|timezone|currencies|source-quality|missingness|method|limits;unknown=null;never-invent`
`PIPE:raw-immutable→source-register→normalize-with-original-values→dedupe→conflict-register→validate→coverage→metrics→context→handoff`
`EVIDENCE:every-numeric/context-claim→source-ID+locator+observation-date+evidence-kind;direct-source>retrieved-chat-reconstruction;reported≠broker-confirmed;derived=inputs+formula;inferred=label;conflicts=retain-both`
`IDENTITY:broker+account-alias+mode+position-ID;fills/orders≠positions;partial-fills=events;no-auto-merge-on-similar-price/date;no-ID→stable-candidate-ID+manual-link-evidence`
`TYPE:actual-live|actual-demo|paper|backtest|hypothetical|account-event|strategy-rule|unknown;analyze-separately;do-not-promote-plan-to-execution`
`NUM:decimal-money;explicit-currency+units;preserve-timezone+original-timestamp;FX-only-with-rate+date+source;no-float-money-totals;no-contract-multiplier-inference`
`QA:duplicates|chronology|side|quantity|fees-sign|gross/net-convention|currency|closed-vs-open|cash-flow-reconciliation|field-coverage;anomaly→flag-not-silent-fix`
`REPORT:found-vs-expected|field-completeness|verified/reported-counts|period|missing-exports|unread/blocked-sources;small-sample=describe-not-prove-edge;no-four-sigma/trading-performance-claim-from-software-tests`
`PERSIST:compact-policy-in-Git;private-history+raw-evidence-in-user-files;Git-publicity-check-before-personal-data;never-store-secrets/full-account-number`
`ACTION:read/analyze=authorized;placing/cancelling-trades/transfers/account-changes=separate-scoped-authorization`
`HISTORY:modules/data_analysis/history_index.json=dated-pointers+coverage;fetch-summary-first;per-trade→archive-SQLite/events;empty-trades-table≠no-history;do-not-redig-already-indexed-sources-without-new-evidence`
`ENRICH:tools/reconcile_history.py=local-indexed-candidate-associations;exact-money+symbol+side+exit;explicit-mail-timezone+bounded-clock-shifts;require-reciprocal-uniqueness-to-label-single;even-single≠verified-position;retain-original-money/currency/risk;R=annotation≠realized-R`

This module provides a reproducible analysis contract, not an autonomous trading engine. Date-specific user statements remain historical reports; they do not establish today's account balance or risk policy.
