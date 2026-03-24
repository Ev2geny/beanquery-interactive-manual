# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beanquery",
#     "beancount",
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(heading):
    title_hd = heading(1, "Interactive beanquery manual", number=False)
    title_hd
    return (title_hd,)


@app.cell
def _(mo):
    mo.md("""
    <style>
    h1, h2, h3, h4, h5 {
        margin-top: 0.1em;
        margin-bottom: 0.1em;
    }
    </style>
    """)
    return


@app.cell(hide_code=True)
def _():
    import io

    from beancount.loader import load_string
    from beancount.core import display_context
    from beancount.parser import printer as bc_printer

    from beanquery.query import run_query
    from beanquery.query_render import render_text

    import marimo as mo

    HEADING_COLOR = "#1e40af"
    _heading_counters = [0, 0, 0, 0]  # h2, h3, h4, h5

    def heading(level: int, text: str, number: bool = True) -> mo.Html:
        """Render a colored markdown heading with optional hierarchical numbering.

        Numbering starts from level 2 (level 1 is reserved for title).
        """
        prefix = ""
        if number and 2 <= level <= len(_heading_counters) + 1:
            idx = level - 2  # 0=h2, 1=h3, 2=h4
            _heading_counters[idx] += 1
            # Reset child counters
            for i in range(idx + 1, len(_heading_counters)):
                _heading_counters[i] = 0
            prefix = ".".join(str(_heading_counters[i]) for i in range(idx + 1)) + ". "
        return mo.md(
            f"<h{level} style='color: {HEADING_COLOR}; margin-top: 0.1em !important; margin-bottom: 0.1em !important;'>"
            f"{prefix}{text}</h{level}>"
        )

    def get_beanquery_output(ledger_text: str, query: str) -> str:
        """
        Executes a BeanQuery command on a ledger string and returns output as text.

        Args:
            ledger_text (str): Beancount ledger as text
            query (str): BeanQuery query

        Returns:
            str: formatted output (or formatted error)
        """

        # 1. Parse ledger
        entries, errors, options_map = load_string(ledger_text)

        if errors:
            buf = io.StringIO()
            bc_printer.print_errors(errors, file=buf)
            return buf.getvalue()

        # 2. Run query
        dcontext = display_context.DisplayContext()

        try:
            rtypes, rrows = run_query(entries, options_map, query)

            buf = io.StringIO()
            render_text(rtypes, rrows, dcontext, buf)

            return buf.getvalue()

        except Exception as e:
            return f"BeanQuery error: {type(e).__name__}: {e}"

    def query_output(ledger_text: str, query: str) -> mo.Html:
        """
        Runs a BeanQuery and returns the result as a marimo plain_text element.

        Args:
            ledger_text: Beancount ledger as text
            query: BeanQuery query string

        Returns:
            mo.Html: formatted output for display
        """
        return mo.plain_text(get_beanquery_output(ledger_text, query))


    def ledger_editor(default_text: str, label: str = ""):
        """
        Creates a marimo code editor for the ledger.
        Defined mainly for future extensibility (e.g. beancount syntax highlighting, etc.)
        Args:
            default_text: initial text for the editor
            label: label for the editor

        Returns:
            mo.ui.UIElement: the code editor UI element
        """
        # TODO: add beancount syntax highlighting
        ui = mo.ui.code_editor(default_text, label=label, show_copy_button=True, debounce=True)
        return ui

    def query_editor(default_text: str, label: str = ""):
        """
        Creates a marimo code editor for the query.
        Defined mainly for future extensibility (e.g. beanquery syntax highlighting, etc.)

        Args:
            default_text: initial text for the editor
            label: label for the editor

        Returns:
            mo.ui.UIElement: the code editor UI element
        """
        ui = mo.ui.code_editor(default_text, language="sql", label=label, show_copy_button=True, min_height=1, debounce=True)
        return ui

    return heading, ledger_editor, mo, query_editor, query_output


@app.cell(hide_code=True)
def _(heading, title_hd):
    _=title_hd
    intro_hd =heading(2, "Introduction to this document", number=True)
    intro_hd
    return (intro_hd,)


@app.cell
def _(heading, intro_hd):
    _=intro_hd
    purpose_hd =heading(3, "Purpose and scope", number=True)
    purpose_hd
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The purpose of this document is to be an interactive and updated to the beanquery v3 replacement of the [Beancount Query Language](https://docs.google.com/document/d/1s0GOZMcrKKCLlP29MD7kHO4L88evrwWdIO0p4EwRBE0/edit?usp=sharing) document
    """)
    return


@app.cell(hide_code=True)
def _(heading, intro_hd):
    # This is a workarount to enforce the sequence of the header executions, as marimo 
    # does not necessarily execute the cells in the top-to-bottom order, 
    # and the header numbering relies on the execution order.
    _=intro_hd
    how_to_use__man_h =heading(3, "How to use the manual")
    how_to_use__man_h
    return (how_to_use__man_h,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You can read the manual as a normal text document.
    You can also change the default both ledger and query inputs.
    As soon an input widget will lose focus, a query will be re-executed and output output will be updated
    """)
    return


@app.cell
def _(heading, how_to_use__man_h):
    _ = how_to_use__man_h
    int_beanquery_hd = heading(2, "Introduction to beanquery", number=True)
    int_beanquery_hd
    return (int_beanquery_hd,)


@app.cell
def _(mo):
    mo.md(r"""
    Beancount’s parsed list of entries is like an in-memory database represented in a form of several tables. Beanquery is a command-line tool that acts like a client to that in-memory database in which you can type queries in a variant of SQL. You invoke it like this:

    ```shell
    bean-query  test.bean
    Input file: "Beancount"
    Ready with 3 directives (2 postings in 1 transactions, 0 validation errors)
    beanquery>
    ```
    Beanquery started as an experiment in beancount v2, but in v3 (when **bean-report** and **bean-web** have been discontinued) became practically the only tool to query information out of beancount ledger. Thus one can say, that in v3 beancount has moved towards the [Self-service business intelligence](https://www.techtarget.com/searchbusinessanalytics/definition/self-service-business-intelligence-BI) model instead of providing off the shelf ready to use reports.
    """)
    return


@app.cell(hide_code=True)
def _(heading, int_beanquery_hd):
    _prev = int_beanquery_hd
    how_to_install_h = heading(2, "How to install beanquery")
    how_to_install_h
    return (how_to_install_h,)


@app.cell
def _(mo):
    mo.md(r"""
    `
    pip install beanquery
    `
    """)
    return


@app.cell
def _(heading, how_to_install_h):
    _prev = how_to_install_h
    how_to_start_h = heading(2, "How to run beanquery")
    how_to_start_h
    return (how_to_start_h,)


@app.cell
def _(mo):
    mo.md(r"""
    To run beanquery type

    ```shell
    beanquery [OPTIONS] FILENAME [QUERY]...
    ```

    **Result:** beanquery will load ledger and start the beanquery client

    e.g.:

    ```shell
    bean-query  test.bean
    Input file: "Beancount"
    Ready with 3 directives (2 postings in 1 transactions, 0 validation errors)
    beanquery>
    ```

    You can also start beanquery as a python module

    ```shell
    python -m beanquery [OPTIONS] FILENAME [QUERY]...
    ```
    """)
    return


@app.cell
def _(heading, how_to_start_h):
    _prev = how_to_start_h
    how_to_get_help_h = heading(2, "How to get help")
    how_to_get_help_h
    return (how_to_get_help_h,)


@app.cell
def _(mo):
    mo.md(r"""
    To get a help from the built in system, type `.help` when in the beanquery client

    ```shell
    beanquery> .help

    Shell utility commands (type help <topic>):
    ===========================================
    EOF    describe  exit     format  history  parse  reload  set
    clear  errors    explain  help    output   quit   run     tables

    Beancount query commands:
    =========================
    balances  from  journal  print  select  targets  where

    beanquery>
    ```

    To get help on a specific command type .help `<command name>`

    E.g.:

    ```
    beanquery> .help select
    Extract data from a query on the postings.

    The general form of a SELECT statement loosely follows SQL syntax, with
    some mild and idiomatic extensions:
    .........

    ```


    To get a list of the tables, available for beancount type `.tables`

    ```shell
    beanquery> .tables
    accounts
    balances
    commodities
    documents
    entries
    events
    notes
    postings
    prices
    transactions
    beanquery>
    ```

    To see list of columns, available in every table type `.describe <table name>`

    e.g. to see list of columns in the **postigs** table type

    ```shell
    beanquery> .describe postings
    table postings:
      type (str)
      id (str)
      date (date)
      year (int)
      month (int)
      day (int)
      filename (str)
      lineno (int)
      location (str)
      flag (str)
      payee (str)
      narration (str)
      description (str)
      tags (set)
      links (set)
      posting_flag (str)
      account (str)
      other_accounts (set)
      number (decimal)
      currency (str)
      cost_number (decimal)
      cost_currency (str)
      cost_date (date)
      cost_label (str)
      position (position)
      price (amount)
      weight (amount)
      balance (inventory)
      meta (dict)
      entry (transaction)
      accounts (set[str])
    beanquery>
    ```
    To see the list of columns in the **transactions** table type:

    ```shell
    beanquery> .describe transactions
    table transactions:
      meta (metadata)
      date (date)
      flag (str)
      payee (str)
      narration (str)
      tags (set)
      links (set)
      accounts (set[str])
    beanquery>
    ```
    """)
    return


@app.cell
def _(heading, how_to_get_help_h):
    _ = how_to_get_help_h
    making_hd=heading(2, "SELECT Queries", number=  True)
    making_hd
    return (making_hd,)


@app.cell
def _(heading, making_hd):
    _= making_hd
    select_intro_hd=heading(3, "Introduction", number=  True)
    select_intro_hd
    return (select_intro_hd,)


@app.cell
def _(mo):
    mo.md(r"""
    The beanquery SELECT query loosely follows standard SQL syntax and can be applied to the set tables list of which can be derived by issuing the `.tables` command.

    ```shell
    beanquery> .tables
    accounts
    balances
    commodities
    documents
    entries
    events
    notes
    postings
    prices
    transactions
    beanquery>
    ```

    List of fields in every table can be obtained using the `.describe <table_name>` command

    It is relatively easy therefore for anyone familiar with SQL to extract needed information, but several caveats / confusions need to be noted.

    **Note:** for someone, not familiar with SQL, some of the material, described in this paragraph, may not be clear, as it refers to the information described further in details, in this case skip the material, which is not clear and come back to it later.
    """)
    return


@app.cell
def _(heading, select_intro_hd):
    _ = select_intro_hd
    caviats_hd = heading(4, "Caveats", number=True)
    caviats_hd
    return (caviats_hd,)


@app.cell
def _(caviats_hd, heading):
    _ = caviats_hd
    trad_vs_had_table_hd = heading(5, "Traditional vs #table syntax", number=True)
    trad_vs_had_table_hd
    return


@app.cell
def _(mo):
    mo.md(r"""
    Originally **beanquery** was designed to be use to query postings table only. In this situation the **FROM** part of the SQL query was "hijacked" to be used for transaction-level filtering and **WHERE** was used for posting-level filtering, which introduced so-called  two-level filtering syntax

    So, the SELECT query structure looked like this:

    ```text
    SELECT [DISTINCT] [<targets>|*]
    [FROM <entry-filter-expression> [OPEN ON <date>] [CLOSE [ON <date>]] [CLEAR]]
    [WHERE <posting-filter-expression>]
    [GROUP BY <groups>]
    [ORDER BY <groups> [ASC|DESC]]
    [LIMIT num]
    ```

    Let us call is the traditional query form.

    **Example:**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Later on, in beancount v3, beanquery was extended to query more tables (see above), in this situation the FROM part was needed again to select a table, so the new form of the SELECT query was introduced

    ```text
    SELECT [DISTINCT] [<targets>|*]
    [FROM #<table-name>]
    [WHERE <posting-filter-expression>]
    [GROUP BY <groups>]
    [ORDER BY <groups> [ASC|DESC]]
    [LIMIT num]
    ```
    Let us call it the **#table** form.

    Note, that:
    * The **#table** form is activated by adding the # symbol in front of the table name
    * The **#table** form allows to query tables, different from postings table, but in case it is used to query postings table (which is possible), it lacks some functionality, available in the traditional form, namely the `[OPEN ON <date>] [CLOSE [ON <date>]] [CLEAR]` part. Later about this functinality later.

    At the moment beanquery supports both query types. Let us explore this on a simple ledger
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Assets:Cash USD
    2023-01-01 open Expenses:Food USD

    2023-01-01 * "Shopping 1"
      Expenses:Food   10 USD
      Assets:Cash    -10 USD

    2023-01-02 * "Shopping 2"
      Expenses:Food   20 USD
      Assets:Cash    -20 USD
      """

    simple_ledger_ui = ledger_editor(_ledger, label="Ledger:")
    simple_ledger_ui
    return (simple_ledger_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT *
    WHERE account = "Expenses:Food"

    """
    sql_ui_traditional = query_editor(_sql, label="Traditional query  (always on postings). Here we select postings to the account Expenses:Food")
    sql_ui_traditional
    return (sql_ui_traditional,)


@app.cell
def _(query_output, simple_ledger_ui, sql_ui_traditional):
    query_output(simple_ledger_ui.value, sql_ui_traditional.value) 
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT *
    FROM #postings
    WHERE account = "Expenses:Food"
    """
    sql_ui_hash_table = query_editor(_sql, label="The same \#table syntax query on postings")
    sql_ui_hash_table
    return (sql_ui_hash_table,)


@app.cell
def _(query_output, simple_ledger_ui, sql_ui_hash_table):
    query_output(simple_ledger_ui.value, sql_ui_hash_table.value) 
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT account, open.date
    FROM #accounts
    """
    sql_ui_hash_table_accounts = query_editor(_sql, label="\# table syntax query on accounts (only \#table style can be used for accounts table)")
    sql_ui_hash_table_accounts
    return (sql_ui_hash_table_accounts,)


@app.cell
def _(query_output, simple_ledger_ui, sql_ui_hash_table_accounts):
    query_output(simple_ledger_ui.value, sql_ui_hash_table_accounts.value) 
    return


@app.cell
def _(caviats_hd, heading):
    _=caviats_hd
    posting_vs_transaction_hd_fields = heading(5, "Posting fields vs transaction fields", number=True)
    posting_vs_transaction_hd_fields
    return (posting_vs_transaction_hd_fields,)


@app.cell
def _(mo):
    mo.md(r"""
    The structure of transactions and entries can be explained by the following simplified diagram:
    """)
    return


@app.cell
def _(mo):
    mo.image("images/transaction_postings.png", alt="Diagram of transactions and postings")
    return


@app.cell
def _(mo):
    mo.md(r"""
    The contents of a ledger is parsed into a list of directives, most of which are “Transaction” objects which contain two or more “Posting” objects. Postings are always linked only to a single transaction (they are never shared between transactions). Each posting refers to its parent transaction but has a unique account name, amount and associated lot (possibly with a cost), a price and some other attributes. The parent transaction itself contains a few useful attributes as well, such as a date, the name of a payee, a narration string, a flag, links, tags, etc.

    So, one can think, that such attribute as **date** or **narration** belong to transaction object, whilst attributes like **account** belongs to posting object. However (at least in the latest version of beanquery) all of the transaction-level fields are also made avaiable in the posting objects (the only exeption being the transaction meta, which is not available from the posting). One can check this by comparing the outputs of the **`.describe postings`** and **`.describe transactions`** commands.

    So, from the beanquery data model the diagram looks more like this
    """)
    return


@app.cell
def _(mo):
    mo.image("images/transaction_postings_v2.png", alt="Diagram of transactions and postings from beanquery perspective")
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Assets:Cash USD
    2023-01-01 open Expenses:Food USD

    2023-01-01 * "Shopping 1"
      Expenses:Food   10 USD
      Assets:Cash    -10 USD

    2023-01-02 * "Shopping 2"
      Expenses:Food   20 USD
      Assets:Cash    -20 USD
      """

    ledger_ui_post_vs_tr = ledger_editor(_ledger, label="Ledger:")
    ledger_ui_post_vs_tr
    return (ledger_ui_post_vs_tr,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT *
    FROM date = 2023-01-01
    """
    sql_ui_trans_level = query_editor(_sql, label="Let us use transaction-level filtering to filter posting at the date 2023-01-01")
    sql_ui_trans_level
    return (sql_ui_trans_level,)


@app.cell
def _(ledger_ui_post_vs_tr, query_output, sql_ui_trans_level):
    query_output(ledger_ui_post_vs_tr.value, sql_ui_trans_level.value)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT *
    WHERE date = 2023-01-01
    """
    sql_ui_posting_level = query_editor(_sql, label="The same result at posting level filtering")
    sql_ui_posting_level
    return (sql_ui_posting_level,)


@app.cell
def _(ledger_ui_post_vs_tr, query_output, sql_ui_posting_level):
    query_output(ledger_ui_post_vs_tr.value, sql_ui_posting_level.value)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Conclusion:** at the moment there seems to be [little reason](https://groups.google.com/g/beancount/c/HVK3_6p1FjM) to use the FROM clause transaction level-filtering in the SELECT query, as everything can be done in the WHERE part
    """)
    return


@app.cell
def _(heading, posting_vs_transaction_hd_fields):
    _=posting_vs_transaction_hd_fields
    jointing_posting_transaction_hd = heading(5, "Pre-jointed postings and related transactions", number=True)
    jointing_posting_transaction_hd
    return


@app.cell
def _(mo):
    mo.md(r"""
    Suppose we need to join postings with related transactions (e.g. to access posting meta field)
    In a traditional SQL environment we would probably have to do something like this.

    ```sql
    SELECT
        postings.*,
        transactions.meta
    FROM postings
    JOIN transactions
        ON postings.transaction_id = transactions.id
    ```
    Beanquery however does not support [yet](https://groups.google.com/g/beancount/c/O0x0eZEp-Lk/m/WFnOS_flEQAJ) table joining, from the other side postings table returns records that include a reference to the transaction that contains them (so, they are kind of pre-joint already).

    One can check this by issuing the `.describe postings` command:

    ```shell
    beanquery> .describe postings
    table postings:
      ....
      entry (transaction)    <== this is a reference to the transaction from the posting
      accounts (set[str])
    beanquery>
    ```
    Let us see, how we can do this my pulling both transaction meta and postings meta:
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Assets:Cash USD
    2023-01-01 open Expenses:Food USD

    2023-01-01 * "Shopping 1"
      my_meta: "tr1_meta"     ; <= transaction-level meta
      Expenses:Food   10 USD
      my_meta: "tr1_posting1" ; <= posting-level meta
      Assets:Cash    -10 USD
      my_meta: "tr1_posting2" ; <= posting-level meta again

    2023-01-02 * "Shopping 2"
      my_meta: "tr2_meta"
      Expenses:Food   20 USD
      my_meta: "tr2_posting1"
      Assets:Cash    -20 USD
      my_meta: "tr2_posting1"
      """

    ledger_ui_with_meta = ledger_editor(_ledger, label="Ledger:")
    ledger_ui_with_meta
    return (ledger_ui_with_meta,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
      date, narration, account, 
      meta['my_meta'] as posting_meta, 
      entry.meta['my_meta'] as trans_meta
    """
    sql_ui_trans_meta = query_editor(_sql, label="Pulling both transaction-level and posting-level meta together")
    sql_ui_trans_meta
    return (sql_ui_trans_meta,)


@app.cell
def _(ledger_ui_with_meta, query_output, sql_ui_trans_meta):
    query_output(ledger_ui_with_meta.value, sql_ui_trans_meta.value)
    return


@app.cell
def _(heading, posting_vs_transaction_hd_fields):
    _=posting_vs_transaction_hd_fields
    select_q_conclusions_hd = heading(4, "Conclusions on using the SELECT Queries", number=True)
    select_q_conclusions_hd
    return


@app.cell
def _(mo):
    mo.md(r"""
    From everything mentioned above one can probably make the following practical conclusions on usage of the SELECT query in beancount.

    * use traditional form of the beanquery query on postings
    * use the #table form for all other tables
    * no particular need to use the **FROM** - clause filtering, as all the fields are also available for the **WHERE** clause
    """)
    return


if __name__ == "__main__":
    app.run()
