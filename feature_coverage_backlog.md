# Beanquery features not yet covered in the manual

Generated 2026-06-10 by comparing the beanquery source code in `references/beanquery_source_code`
(grammar `bql.ebnf`, `query_env.py`, `shell.py`, `sources/beancount.py`, CLI, `CHANGES.rst`)
against `manual.py`. Sorted from most to least important from a reader's perspective.
Work through one item at a time; check off when covered in the manual.

## Backlog

- [x] **1. `PIVOT BY` clause** — fully implemented in beanquery (grammar + `compiler.py:314`, `EvalPivot`),
  but section 18.1 of the manual explicitly claims "No PIVOT functionality". Outdated misinformation —
  needs correcting, not just expanding. Highest priority.
  *Done 2026-06-10: new section 13.5 with four interactive examples; PIVOT BY added to both
  SELECT syntax blocks in section 8; section 18.1 claim removed (18.2 renumbered to 18.1).*

- [ ] **2. Named queries: ledger `query` directive + `.run` shell command** — queries stored in the
  Beancount file can be executed with `.run name` / `.run *` (tab completion; the query directive's
  date becomes the default CLOSE date). Very practical daily-workflow feature, never mentioned.

- [ ] **3. `VALUE()` and `GETPRICE()` functions** — market-value conversion using the price map.
  Siblings of `CONVERT()` (which has section 12.2.3). `VALUE()` is essential for the Net-Worth
  use case shown in 19.2.
  *VALUE() done 2026-06-20: new section 12.2.4 (after CONVERT), with a basic mark-to-market
  example and a side-by-side VALUE()/CONVERT() comparison; following 12.2.x sections renumbered.
  GETPRICE() still outstanding.*

- [ ] **4. Type-casting functions `int()`, `decimal()`, `str()`, `bool()`, `date()`** (incl. `date(y, m, d)`) —
  added specifically to handle the generic `object` type returned by metadata functions (covered in 12.2.9).
  The coalesce example (~line 3562) already uses `str(meta['project'])` without explaining casting.

- [ ] **5. The seven other tables in detail** — `accounts`, `commodities`, `prices`, `balances`
  (with `diff_amount` → `discrepancy` column rename), `notes`, `events`, `documents` are only
  name-listed in section 6; section 10 covers only `postings` and `transactions`.
  At minimum `accounts` and `prices` deserve examples.

- [ ] **6. Date helper functions** — `year()`, `month()`, `day()`, `quarter()`, `yearmonth()`, `weekday()`,
  `today()`, `date_add()`, `date_diff()`, `parse_date()`, plus date attribute access (`date.year`).
  The manual covers `date_part`/`date_trunc`/`date_bin`/`interval` but not these simpler everyday ones;
  the example at ~line 3105 already uses `today()` undocumented.

- [ ] **7. Account-related functions** — `parent()`, `leaf()` (only `root()` is documented),
  `open_date()`, `close_date()`, `open_meta()`, `commodity_meta()`, `account_sortkey()`, `has_account()`.
  `open_date`/`close_date` particularly useful for reports.

- [ ] **8. String functions** — `upper()`, `lower()`, `substr()`, `maxwidth()`, `splitcomp()`, `grep()`,
  `grepn()`, `subst()`, `length()`, `repr()`. (The "substr" mentions currently in the manual are the
  `IN` substring operator, not the function.)

- [ ] **9. Inventory/Amount helper functions** — `number()`, `currency()`/`commodity()`, `only()`,
  `empty()`, `filter_currency()`, `possign()`, `abs()`, `neg()`, `round()`, `safediv()`,
  `findfirst()`, `joinstr()`.

- [ ] **10. Shell commands beyond `.help`/`.describe`/`.tables`/`.set`** — `.explain` (shows parse tree,
  compiled query, target types — great for debugging), `.format`, `.output FILE`, `.history`, `.clear`,
  `.errors`, `.reload`, `.parse`; plus the init file (`BEANQUERY_INIT`, default
  `~/.config/beanquery/init`) and history file (`BEANQUERY_HISTORY`). They appear in the `.help`
  output excerpt in section 5 but are never explained.

- [ ] **11. CLI options and output formats** — section 4 never enumerates `-f/--format`, `-o/--output`,
  `-m/--numberify`, `-q/--no-errors`, reading a query from stdin, or format inference from the output
  filename. Also the third render format **`beancount`** (Appendix A only lists "text", "csv") —
  which is what `PRINT` uses internally.

- [ ] **12. Python DB-API / placeholders** — `beanquery.connect()`, cursors, parameterized queries with
  `%s` / `%(name)s` placeholders (paramstyle `pyformat`). Would naturally fill the empty section 17
  (Data Frames, marked `#TODO`).

- [ ] **13. `CREATE TABLE` / `INSERT INTO` and the in-memory table source** — in the grammar and
  `sources/memory.py`. Experimental; low reader priority.

- [ ] **14. CSV data source** — attaching `csv:file.csv` as a queryable table (`sources/csv.py`),
  with type guessing. Niche, but relevant to the "no table joining" workaround discussion in 18.2.

- [ ] **15. Minor syntax details** — BQL comments (`/* ... */` blocks and `;` line comments),
  quoted identifiers for column names, `.describe` on structured types
  (`.describe amount`, `position`, `cost`, `date`).

## Side findings (small fixes, not new sections)

- [x] Section 18.1 inaccuracy: PIVOT BY exists (see item 1). *Fixed 2026-06-10 together with item 1.*
- [ ] Appendix A `??` placeholders: `nullvalue` is the string printed in place of NULL values;
  `unicode` makes the text renderer use Unicode box-drawing characters.
- [ ] Section 13.2 (ORDER BY): per the changelog, NULLs always sort smaller than any other value —
  worth a sentence.
