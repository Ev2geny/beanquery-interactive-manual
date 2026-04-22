# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beancount",
#     "beanquery>=0.2.0",
#     "marimo>=0.22.4",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium", css_file="custom.css")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <a href="https://github.com/Ev2geny/beanquery_interactive_manual" target="_blank">
      <img src="https://img.shields.io/badge/GitHub-Ev2geny%2Fbeanquery__interactive__manual-blue?logo=github" alt="GitHub repository"/>
    </a>

    # Interactive beanquery manual
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    import tomllib
    from pathlib import Path
    _pyproject_path = Path(__file__).parent / "pyproject.toml"
    with open(_pyproject_path, "rb") as _f:
        _version = tomllib.load(_f)["project"]["version"]
    mo.md(f"*Version: {_version}*")
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo

    import io

    from beancount.loader import load_string
    from beancount.core import display_context
    from beancount.parser import printer as bc_printer

    from beanquery.query import run_query
    from beanquery.query_render import render_text


    def get_beanquery_output(ledger_text: str, query: str, narrow: bool = True) -> str:
        entries, errors, options_map = load_string(ledger_text)

        if errors:
            buf = io.StringIO()
            bc_printer.print_errors(errors, file=buf)
            return buf.getvalue()

        try:
            rtypes, rrows = run_query(entries, options_map, query)

            buf = io.StringIO()
            dcontext = display_context.DisplayContext()

            # -----------------------------------
            # Detect PRINT (entry rows)
            # -----------------------------------
            is_entry_rows = (
                rrows
                and len(rrows[0]) == 1
                and hasattr(rrows[0][0], "meta")
            )

            if is_entry_rows:
                # PRINT output
                entries = [row[0] for row in rrows]
                bc_printer.print_entries(entries, file=buf)
            else:
                # SELECT output
                render_text(rtypes, rrows, dcontext, buf, narrow=narrow)

            return buf.getvalue()

        except Exception as e:
            parseinfo = getattr(e, 'parseinfo', None)
            if parseinfo is not None:
                pos = parseinfo.pos
                endpos = parseinfo.endpos
                lineno = parseinfo.line
                text = parseinfo.tokenizer.text
                lines = text.splitlines(True)
                col = pos
                for line in lines[:lineno]:
                    col -= len(line)
                out = [f"error: {e}"]
                strip = True
                for line in lines[:lineno]:
                    if strip and not line.rstrip():
                        continue
                    strip = False
                    out.append('| ' + line.rstrip().expandtabs())
                out.append('| ' + lines[lineno].rstrip().expandtabs())
                out.append('| ' + ' ' * col + '^' * max(1, endpos - pos))
                return '\n'.join(out)
            return f"error: {type(e).__name__}: {e}"

    def query_output(ledger_text: str, query: str, narrow: bool = False) -> mo.Html:
        """
        Runs a BeanQuery and returns the result as a marimo plain_text element.

        Args:
            ledger_text: Beancount ledger as text
            query: BeanQuery query string
            narrow: When True, truncate column headers to the width of the data
                    (equivalent to the beanquery shell's 'narrow' variable).

        Returns:
            mo.Html: formatted output for display
        """
        return mo.plain_text(get_beanquery_output(ledger_text, query, narrow=narrow))


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

    return ledger_editor, mo, query_editor, query_output


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 Introduction to this document
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.1 Purpose and scope
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is an interactive manual and tutorial for [beanquery](https://github.com/beancount/beanquery) — a customizable, extensible, lightweight SQL query tool for [Beancount](https://github.com/beancount/beancount/) ledger data.

    This document is intended as a follow-up to the Beancount v2 [Beancount Query Language](https://docs.google.com/document/d/1s0GOZMcrKKCLlP29MD7kHO4L88evrwWdIO0p4EwRBE0/edit?usp=sharing) document.

    It was created with the following goals in mind:

    * to cover the latest features of beanquery
    * to include many real examples using actual ledgers
    * to be self-documenting: all query outputs are computed by running beanquery as part of the notebook execution
    * to be interactive: when run as a [marimo](https://marimo.io/) notebook, readers can experiment by changing the default ledgers and/or queries, with outputs updating automatically

    **Current state**: work is ongoing
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.2 How to use this manual
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This document assumes no prior knowledge of SQL and is structured as much as possible as a tutorial, where each chapter builds on the material covered in the previous ones. As a result, the material is more spread throughout the document than it would be if it were written for an SQL-familiar reader. For example, the available tables are introduced in one chapter, and more detailed information about some of them is added in several later chapters.

    This document is written as a [marimo](https://docs.marimo.io/) notebook. You can read it as a normal HTML document.
    However, the cool feature of this notebook is that if you run it as a marimo notebook, you can interact with the document by changing the default text for both the ledger and the query in all examples. As soon as an input widget loses focus, the query is re-executed and the output is updated.

    Both in HTML format and in the marimo notebook format, a clickable table of contents is available when hovering near the right side of the browser's vertical scroll bar.
    """)
    return


@app.cell
def _(mo):
    mo.image(src = "images/TOC.png", width="40%")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note that throughout the document, unresolved questions the author had about beanquery functionality are marked with double question marks.

    E.g.: ?? Why do we need this.

    There are also some TODOs, marked with #TODO. E.g.:

    _#TODO: we need to investigate this_
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 Introduction to beanquery
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Beanquery parses a Beancount ledger and creates an in-memory database represented as several tables. Beanquery then exposes a command-line tool that acts as a client to that in-memory database, where you can type queries in a variant of SQL.

    Beanquery started as an experiment in Beancount v2, but in v3 (when **bean-report** and **bean-web** were discontinued) it became practically the only tool for querying information from a Beancount ledger. Thus, one can say that in v3 Beancount has moved toward the [Self-service business intelligence](https://www.techtarget.com/searchbusinessanalytics/definition/self-service-business-intelligence-BI) model, instead of providing off-the-shelf ready-to-use reports.

    So one might ask: why create another SQL client? Why not output the data to an SQLite database and let the user use any SQL client? Apparently this experiment was conducted by creating [bean-sql](https://github.com/beancount/beancount/blob/v2/beancount/scripts/sql.py). It turned out that writing queries was painful and carrying out operations on lots held at cost was difficult.

    Therefore beanquery has some extras that are essential for querying a Beancount ledger. These extras include (but are not necessarily limited to) the following:
    * The client supports the semantics of inventory booking implemented in Beancount. It also supports aggregation functions on inventory objects and rendering functions (e.g., COST() to render the cost of an inventory instead of its contents).
    * The client supports some functions that run on postings but in the background also access other tables (e.g. the CONVERT() function, which formally operates on amounts, positions, or inventories, but in the background also uses the prices table).
    * It allows filtering at two levels simultaneously: you can filter whole transactions, which has the benefit of respecting the accounting equation, and then, usually for presentation purposes, you can also filter at the posting level.
    * Objects in one table already have references to related objects in another table. For example, records in the postings table have a reference to their related transaction object. So one can say that these tables have already been pre-joined (even though technically this is not entirely correct).
    * Transactions can be summarized in a manner useful for producing balance sheets and income statements. For example, our SQL variant explicitly supports a “close” operation with an effect similar to year-end closing, which inserts transactions to clear income statement accounts to equity and removes past history.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 How to install beanquery
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    `
    pip install beanquery
    `
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 How to run beanquery CLI
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    To run beanquery type

    ```shell
    bean-query [OPTIONS] FILENAME [QUERY]...
    ```

    This launches the query tool in interactive mode, where you can enter multiple commands on the dataset loaded in memory. Beanquery parses the input file, prints a few basic statistics about your ledger, and provides a command prompt for you to enter query commands.

    e.g.:

    ```shell
    bean-query  test.bean
    Input file: "Beancount"
    Ready with 3 directives (2 postings in 1 transactions, 0 validation errors)
    beanquery>
    ```

    If your ledger contains any errors, they are printed before the prompt.

    E.g.:

    ```shell
    PS C:\_code\bean> bean-query test.bean
    C:\_code\bean\test.bean:7: syntax error, unexpected ACCOUNT

    Input file: "Beancount"
    Ready with 8 directives (6 postings in 4 transactions, 1 validation errors)
    beanquery>
    ```

    You can also start beanquery as a python module

    ```shell
    python -m beanquery [OPTIONS] FILENAME [QUERY]...
    ```

    If you’d like to run queries directly from the command-line, without an interactive prompt, you can provide the query directly following your filename:

    ```shell
    $ bean-query myfile.beancount 'balances from year = 2014'
                         account                       balance
    ----------------------------------------------------------------------
    … <balances follow> …
    ```

    All the interactive commands are supported.


    **Shell variables**
    The interactive shell has a few “set” variables that you can customize to change some of the behavior of the shell. These are like environment variables. Refer to **Appendix A for more information.**

    Note, that in this document for demonstration purposes the following changes are done to default environmental variables:

    ```
    .set narrow false
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5 How to get help
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    To get help from the built-in system, type `.help` when in the beanquery client

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

    To get help on a specific command type `.help <command name>`

    E.g.:

    ```
    beanquery> .help select
    Extract data from a query on the postings.

    The general form of a SELECT statement loosely follows SQL syntax, with
    some mild and idiomatic extensions:
    .........

    ```


    To get the list of tables available in beanquery, type `.tables`

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

    To see the list of columns available in a table, type `.describe <table name>`

    For example, to see the columns in the **postings** table, type

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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6 Available tables. Introduction
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    The list of tables which beanquery exposes to the user can be derived by issuing the `.tables` command.

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

    The list of fields in every table can be obtained using the `.describe <table_name>` command.

    Note: for the postings table, a more complete list of columns can be obtained using the `.help targets` command.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7 Types of queries
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Beanquery supports the following types of queries, further discussed in this document:

    * SELECT
    * BALANCES
    * JOURNAL
    * PRINT
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8 SELECT Query
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    The beanquery SELECT query loosely follows standard SQL syntax, with some deviations that will be discussed throughout this manual.

    It should be noted that originally **beanquery** was designed to extract information from the postings table only. In this situation the **FROM** part of the SQL query was "hijacked" for transaction-level filtering and **WHERE** was used for posting-level filtering, which introduced a so-called two-level filtering syntax:

    The SELECT query structure looked like this (written in the informal EBNF language):

    ```text
    SELECT [DISTINCT] [<targets>|*]
    [FROM <entry-filter-logical-expression> [OPEN ON <date>] [CLOSE [ON <date>]] [CLEAR]]
    [WHERE <posting-filter-logical-expression>]
    [GROUP BY <groups>]
    [ORDER BY <groups> [ASC|DESC]]
    [LIMIT num]
    ```

    Let us call it the **traditional SELECT query form**.

    /// details | **Note about the informal EBNF language**
        type: info

     In this manual, queries are described using a simplified notation that shows the structure of a command.

    This notation is based on an **informal version of Extended Backus–Naur Form (EBNF)**, but you do not need to know anything about EBNF to use it. It is designed to be easy to read and understand.

     Here is how to interpret it:

    * Words written in **UPPERCASE** are keywords that must be typed exactly as shown
    * Items in **square brackets `[ ... ]`** are optional
    * The symbol `|` means “or” (choose one of the alternatives)
    * Text inside **angle brackets `<...>`** is a placeholder — you replace it with your own value
    * Items written next to each other should be written in that order

    **Example:**

     ```sql
     SELECT [DISTINCT] <targets | * > [FROM <expression>]
     ```

    This means:

     * Start with `SELECT`
     * Optionally add `DISTINCT`
     * Either provide one or more targets (what you want to select) or put asterisks (*)
     * Then optionally put `FROM`, followed by some expression (expressions are discussed later)

    **In simple terms:**

    Think of this syntax as a **template** for writing queries:

    It shows what parts are required, what parts are optional, and where you need to insert your own values.

    ///

    Later, in Beancount v3, when beanquery was moved to a standalone tool, it was extended to query more tables (see above). In this situation the FROM part was needed again to select a table, so a new form of the SELECT query was introduced:

    ```text
    SELECT [DISTINCT] [<targets>|*]
    [FROM #<table-name>]
    [WHERE <posting-filter-logical-expression>]
    [GROUP BY <groups>]
    [ORDER BY <groups> [ASC|DESC]]
    [LIMIT num]
    ```
    Let us call it the **#table** query form.

    Note that:
    * The **#table** form is activated by adding the # symbol in front of the table name
    * The **#table** form allows querying tables other than the postings table, but when used to query the postings table (which is possible), it lacks some functionality available in the traditional form, namely the `[OPEN ON <date>] [CLOSE [ON <date>]] [CLEAR]` part. (This may actually be a [bug](https://github.com/beancount/beanquery/issues/274), rather than a feature.)

    So, to summarize:
    * In the traditional BQL, the FROM clause is used to describe the posting-level filter, not to identify the data source
    * In the **#table** syntax, the table name must be preceded by the # symbol

    Currently beanquery supports both query types. Let us explore this with a simple ledger.
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Income:Salary
    2023-01-01 open Assets:Cash 
    2023-01-01 open Expenses:Food 

    2023-01-01 * "Salary"
      Income:Salary   -100 USD
      Assets:Cash      100 USD

    2023-01-02 * "Shopping 1"
      Expenses:Food   20 USD
      Assets:Cash    -20 USD
      """

    simple_ledger_ui = ledger_editor(_ledger, label="Simple ledger for SELECT query")
    simple_ledger_ui
    return (simple_ledger_ui,)


@app.cell
def _(mo):
    mo.md(r"""
    Let us create a query which shows postings to the account `Expenses:Food`
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT *
    WHERE account = "Expenses:Food"

    """
    sql_ui_traditional = query_editor(_sql, label="Traditional query")
    # sql_ui_traditional
    return (sql_ui_traditional,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT *
    FROM #postings
    WHERE account = "Expenses:Food"
    """
    sql_ui_hash_table = query_editor(_sql, label=r"The same query, but using the \#table syntax")
    # sql_ui_hash_table
    return (sql_ui_hash_table,)


@app.cell
def _(
    mo,
    query_output,
    simple_ledger_ui,
    sql_ui_hash_table,
    sql_ui_traditional,
):
    mo.hstack([
        mo.vstack([
            sql_ui_traditional,
            query_output(simple_ledger_ui.value, sql_ui_traditional.value)
        ]),
        mo.vstack([
            sql_ui_hash_table,
            query_output(simple_ledger_ui.value, sql_ui_hash_table.value)   
        ])

    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    Note, that here we use the wildcard symbol (*) to list some columns, instead of specifying column names manually.

    Difference to SQL: the BQL using a wildcard as the target list (“*”) selects a good default list of columns, whilst the traditional SQL the * is used to describe the complete set of columns, available in the table.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Let us now query the **accounts** table. Note, that for the **accounts** table we have no choice, but to use the **#table** query format.
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT account, open.date, close.date
    FROM #accounts
    """
    sql_ui_hash_table_accounts = query_editor(_sql, label=r"Querying on accounts (only \#table style can be used for the accounts table)")
    sql_ui_hash_table_accounts
    return (sql_ui_hash_table_accounts,)


@app.cell
def _(query_output, simple_ledger_ui, sql_ui_hash_table_accounts):
    query_output(simple_ledger_ui.value, sql_ui_hash_table_accounts.value) 
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9 Expressions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    When we talked about SQL query we mentioned, but not defined the notion of an expression. Let us correct this.

    An **expression** is something, which can be evaluated to a value.

    A **logical expression** is an expression, which can be evaluated to a  logical value (`TRUE` or `FALSE`)

    In beanquery an expression is constructed by combining **table columns**, **constants**, **operators**, and **functions**. All of these elements are described later in this document.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 9.1 Operators
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Common comparison and logical operators are provided to operate on the available data columns:
    * = (equality), != (inequality)
    * < (less than), <= (less than or equal)
    * \> (greater than), >= (greater than or equal)
    * AND (logical conjunction)
    * OR (logical disjunction)
    * NOT (logical negation)
    * IN (set membership)

    Beanquery also provides a regular expression search operator on string objects:
    * ~ (search regexp)

    ?? Which not-logical operators are supported? E.g. I found, that the '+' operator also works. E.g.: `SELECT "a"+"b"`

    The example below demonstrates a few of these operators
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Income:Salary
    2023-01-01 open Assets:Cash 
    2023-01-01 open Expenses:Food 
    2023-01-01 open Expenses:Misc 

    2023-01-01 * "Salary"
      Income:Salary   -100 USD
      Assets:Cash      100 USD

    2023-01-02 * "John" "Shopping 1" #trip-berlin
      Expenses:Food   20 USD
      Assets:Cash    -20 USD

    2023-02-03 * "Richard" "Shopping 2" #trip-london
      Expenses:Misc   20 USD
      Assets:Cash    -20 USD
      """

    operators_ledger_ui = ledger_editor(_ledger, label="Ledger to demonstrate operators")
    operators_ledger_ui
    return (operators_ledger_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
         date, account, payee,narration, position
    WHERE 
          account ~ "^Expenses"
          AND "trip-london" IN tags
          AND NOT payee = "John"
    """
    sql_ui_operators = query_editor(_sql, label=r"Operators demo query")
    sql_ui_operators
    return (sql_ui_operators,)


@app.cell
def _(operators_ledger_ui, query_output, sql_ui_operators):
    query_output(operators_ledger_ui.value, sql_ui_operators.value) 
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 9.2 Constants
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The following types of constants can be entered in the beanquery expression

    * String: `"I am a string"`
    * Date:  Dates are entered in `YYYY-MM-DD format: SELECT * WHERE date < 2024-05-20..`
    * Integer: `1`
    * Boolean: `TRUE, FALSE`
    * Number:  `1.2`
    * Null object: `NULL`       ?? How can we use this NULL in practice?
    * ?? can we enter a set of strings constant in an expression?
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Income:Salary
    2023-01-01 open Assets:Cash 

    2023-01-01 * "Salary"
      Income:Salary   -100 USD
      Assets:Cash      100 USD
      """

    simple_ledger_constants_ui = ledger_editor(_ledger, label="Simple ledger for constants")
    simple_ledger_constants_ui
    return (simple_ledger_constants_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
       "I am a string" as string_const, 
        2026-10-10 as date_const, 
        10 as int_const,  
        NULL as null_const, 
        3.14 as number_const, 
        TRUE as bool_const
    FROM #transactions

    """
    sql_ui_constants = query_editor(_sql, label="Query has no practical sense, but it demonstrates how to enter constants in beanquery")
    sql_ui_constants
    return (sql_ui_constants,)


@app.cell
def _(query_output, simple_ledger_constants_ui, sql_ui_constants):
    query_output(simple_ledger_constants_ui.value, sql_ui_constants.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 9.3 Columns and Functions in expressions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A full list of columns and functions, available to be used to construct expressions are available via the `.help XXX` command:

    * To get a help for the `SELECT` clause expressions type `.help targets`
    * To get a help for the `FROM` clause expressions type `.help FROM`
    * To get a help for the `WHERE` clause expressions type `.help WHERE`

    Example (reduced):

    ```
    beanquery> .help from

    A logical expression that consist of columns on directives (mostly
    transactions) and simple functions.

    Columns
    -------

    id: str
      Unique id of a directive.

    ...

    date: date
      The date of the directive.

    ...

    Functions
    ---------

    abs(decimal)

    convert(amount, str)
    convert(amount, str, date)
    convert(position, str)
    convert(position, str, date)
      Coerce an amount to a particular currency.

    convert(inventory, str)
    convert(inventory, str, date)
      Coerce an inventory to a particular currency.

    ...
    ```

    Note, that the list of table columns (in this example the list of table columns in the transactions table), available via the `.help from` command is broader, then the list of columns available for the same table via the `.describe <table-name>`.

    E.g. in this case the `.describe transactions` does not list the `id` and some other columns, otherwise available for the `FROM ...` clause

    ```text
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
    ?? Why is that

    _#TODO: investigate this and raise an issue, if applicable_
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10 More on tables
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    This section contains some additional information on some of the tables, available in beanquery.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 10.1 The postings table
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    As it was already mentioned, the beanquery was originally created to work with the postings table only, therefore the postings table has some notable and sometimes unexpected features
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 10.1.1 Transactions columns in the postings table
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    The relation between transactions and postings can be explained by the following simplified diagram:
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

    So, one can think that attributes such as **date** or **narration** belong to the transaction object, whilst attributes like **account** belong to the posting object. However (probably for simplicity) all of the transaction-level fields are also made available in the posting objects (the only exception being the transaction meta, which is not available from the posting). One can check this by comparing the outputs of the **`.describe postings`** and **`.describe transactions`** commands.

    So, from the beanquery data model the diagram looks more like this
    """)
    return


@app.cell
def _(mo):
    mo.image("images/transaction_postings_v2.png", alt="Diagram of transactions and postings from beanquery perspective")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let us demonstrate this on a simple ledger
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

    ledger_ui_post_vs_tr = ledger_editor(_ledger, label="Simple ledger:")
    ledger_ui_post_vs_tr
    return (ledger_ui_post_vs_tr,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let us create a query to show all postings for the date of 2023-01-01
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT *
    FROM date = 2023-01-01
    """
    sql_ui_trans_level = query_editor(_sql, label="Using transaction-level filtering")
    # sql_ui_trans_level
    return (sql_ui_trans_level,)


@app.cell
def _():
    # query_output(ledger_ui_post_vs_tr.value, sql_ui_trans_level.value)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT *
    WHERE date = 2023-01-01
    """
    sql_ui_posting_level = query_editor(_sql, label="Using posting level filtering")
    # sql_ui_posting_level
    return (sql_ui_posting_level,)


@app.cell
def _():
    # query_output(ledger_ui_post_vs_tr.value, sql_ui_posting_level.value)
    return


@app.cell
def _(
    ledger_ui_post_vs_tr,
    mo,
    query_output,
    sql_ui_posting_level,
    sql_ui_trans_level,
):
    mo.hstack([
        mo.vstack([
            sql_ui_trans_level,
            query_output(ledger_ui_post_vs_tr.value, sql_ui_trans_level.value)
        ]),
        mo.vstack([sql_ui_posting_level,
        query_output(ledger_ui_post_vs_tr.value, sql_ui_posting_level.value)])
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    We can see that the field `date` can be used both within the FROM clause (transaction-level filter) and the WHERE clause (postings-level filter). This is despite the fact that, logically speaking, the `date` column should be a transaction-level field only.

    **Conclusion:** at the moment there seems to be [little reason](https://groups.google.com/g/beancount/c/HVK3_6p1FjM) to use the FROM clause transaction level-filtering in the SELECT query, as everything can be done in the WHERE part
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 10.1.2 The `entry` column
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Suppose we would need to join postings with related transactions (e.g. to access posting meta field)
    In a traditional SQL environment we would probably have to do something like this.

    ```sql
    SELECT
        postings.*,
        transactions.meta
    FROM postings
    JOIN transactions
        ON postings.transaction_id = transactions.id
    ```
    Beanquery however does not support [yet](https://groups.google.com/g/beancount/c/O0x0eZEp-Lk/m/WFnOS_flEQAJ) table joining. On the other hand, the postings table returns records that include a reference to the transaction that contains them, so they are kind of pre-joined already (in addition to the fact that transaction columns are also available in the postings table).

    One can check this by issuing the `.describe postings` command:

    ```shell
    beanquery> .describe postings
    table postings:
      ....
      entry (transaction)    <== this is a reference to the transaction from the posting
      accounts (set[str])
    beanquery>
    ```
    Let us see how we can do this by pulling both transaction meta and posting meta:
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 10.1.3 The `other_accounts` column
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    The `other_accounts` column is another notable column in the postings table. It contains the set of accounts from other postings in the same transaction.

    Example:
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Income:Salary
    2023-01-01 open Assets:Cash 
    2023-01-01 open Liabilities:CreditCard
    2023-01-01 open Expenses:Food 
    2023-01-01 open Expenses:Misc 

    2023-01-01 * "Salary"
      Income:Salary   -100 USD
      Assets:Cash      100 USD

    2023-01-02 * "Shopping with cash"
      Expenses:Food   10 USD
      Expenses:Misc   10 USD
      Assets:Cash    -20 USD

    2023-01-02 * "Shopping with credit card"
      Expenses:Food             30 USD
      Liabilities:CreditCard   -30 USD
      """

    other_accounts_ledger_ui = ledger_editor(_ledger, label="The `other_accounts` ledger:")
    other_accounts_ledger_ui
    return (other_accounts_ledger_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT  date, account, narration, position, other_accounts
    """
    sql_ui_other_accounts = query_editor(_sql, label="Let us see, what the other_accounts column contains")
    sql_ui_other_accounts
    return (sql_ui_other_accounts,)


@app.cell
def _(other_accounts_ledger_ui, query_output, sql_ui_other_accounts):
    query_output(other_accounts_ledger_ui.value, sql_ui_other_accounts.value)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Let us now use the `other_accounts` column to select all expenses that were paid with cash rather than with a credit card.
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT  date, account, narration, position
    WHERE  account ~ '^Expenses' AND'Assets:Cash' IN other_accounts
    """
    sql_ui_other_accounts_cash = query_editor(_sql, label="Expenses, paid with cash")
    sql_ui_other_accounts_cash
    return (sql_ui_other_accounts_cash,)


@app.cell
def _(other_accounts_ledger_ui, query_output, sql_ui_other_accounts_cash):
    query_output(other_accounts_ledger_ui.value, sql_ui_other_accounts_cash.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 10.1.4 The `balance` column
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One common desired output is a journal of entries over time (also called a “register” in Ledger).
    For this type of report, it is convenient to also render a column of the cumulative balance of the selected postings rows. Access to the previous row is not a standard SQL feature, so we get a little creative and provide a special column called “balance” which is automatically calculated based on the previous selected rows. This provides the ability to render typical account statements such as those mailed to you by a bank. Output might look like this:
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Income:Salary
    2023-01-01 open Assets:Bank-A
    2023-01-01 open Assets:Bank-B
    2023-01-01 open Expenses:Misc 

    2023-01-01 * "Salary"
      Income:Salary   -1000 USD
      Assets:Bank-A    750 USD
      Assets:Bank-B    250 USD

    2023-01-02 * "Shopping using Bank-A"
      Expenses:Misc    100 USD
      Assets:Bank-A   -100 USD

    2023-01-03 * "Shopping using Bank-B"
      Expenses:Misc    110 USD
      Assets:Bank-B   -110 USD

    2023-01-04 * "Shopping using Bank-A again"
      Expenses:Misc    120 USD
      Assets:Bank-A   -120 USD
      """

    balance_ledger_ui = ledger_editor(_ledger, label="The `balance` ledger:")
    balance_ledger_ui
    return (balance_ledger_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT  date, account, narration, position, balance
    WHERE account = "Assets:Bank-A"
    """
    sql_ui_balance = query_editor(_sql, label="Bank-A balance over time")
    sql_ui_balance
    return (sql_ui_balance,)


@app.cell
def _(balance_ledger_ui, query_output, sql_ui_balance):
    query_output(balance_ledger_ui.value, sql_ui_balance.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note, that the beanquery starts counting balance from 0 and takes into account all postings, which pass through the filter. Therefore if the goal is to have a bank equivalent balance information, then one shall not put any filters, which would filter out any postings to the bank account account. E.g. if we put a filter to start later, then the result would be different.

    Also selecting more than 1 bank account would create a result, different from what you get from your bank statement:
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT  date, account, narration, position, balance
    WHERE account = "Assets:Bank-A" AND date > 2023-01-01
    """
    sql_ui_balance_start_later = query_editor(_sql, label="Bank-A balance, starting later")
    # sql_ui_balance_start_later
    return (sql_ui_balance_start_later,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT  date, account, narration, position, balance
    WHERE account = "Assets:Bank-A" OR account = "Assets:Bank-B"
    """
    sql_ui_balance_more_than_1 = query_editor(_sql, label="Bank-A, Bank-B balance over time")
    # sql_ui_balance_more_than_1
    return (sql_ui_balance_more_than_1,)


@app.cell
def _(
    balance_ledger_ui,
    mo,
    query_output,
    sql_ui_balance_more_than_1,
    sql_ui_balance_start_later,
):
    mo.hstack([
        mo.vstack([
            sql_ui_balance_start_later,
            query_output(balance_ledger_ui.value, sql_ui_balance_start_later.value)   
        ]),
        mo.vstack([
            sql_ui_balance_more_than_1,
            query_output(balance_ledger_ui.value, sql_ui_balance_more_than_1.value)   
        ])
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 10.1.5 The `weight` column
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The computed weight used for this posting

    _#TODO: add expamples_
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 10.2 Transactions table
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 10.2.1 The `id` column
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    A special column exists that identifies each transaction uniquely: “id”. It is a unique hash automatically computed from the transaction and should be stable between runs.
    This hash is derived from the contents of the transaction object itself (if you change something about the transaction, e.g. you edit the narration, the id will change).

    Note: even though the `id` field logically belongs to the transaction, it is not available in the `transactions` table. The only way to find it is to look in postings via traditional query.
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Income:Salary
    2023-01-01 open Assets:Cash 
    2023-01-01 open Expenses:Food 

    2023-01-01 * "Salary"
      Income:Salary   -100 USD
      Assets:Cash      100 USD

    2023-01-02 * "Shopping 1"
      Expenses:Food   10 USD
      Assets:Cash    -10 USD

    2023-01-02 * "Shopping 2"
      Expenses:Food   20 USD
      Assets:Cash    -20 USD
      """

    ledger_id_ui = ledger_editor(_ledger, label="Simple ledger for to test id column")
    ledger_id_ui
    return (ledger_id_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT  date, account, narration, position, id
    """
    sql_ui_id_postings = query_editor(_sql, label="Show some columns including the id column")
    sql_ui_id_postings
    return (sql_ui_id_postings,)


@app.cell
def _(ledger_id_ui, query_output, sql_ui_id_postings):
    query_output(ledger_id_ui.value, sql_ui_id_postings.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Once the `id` field is known, one can use it also for the transaction - level filtering.  E.g. one can use the `PRINT` query (discussed later) to print the specific entry. This can be useful during debugging.
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    PRINT from id = '5801fa0babefb50972631ce070888875'
    """
    sql_ui_id_print = query_editor(_sql, label="PRINT specific entry by id")
    sql_ui_id_print
    return (sql_ui_id_print,)


@app.cell
def _(ledger_id_ui, query_output, sql_ui_id_print):
    query_output(ledger_id_ui.value, sql_ui_id_print.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 11 Practical conclusions on using the SELECT Query
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    From everything mentioned above one can probably make the following practical conclusions on usage of the SELECT query in beancount.

    * use traditional form of the beanquery query on postings
    * use the #table form for all other tables
    * no particular need to use the **FROM** - clause filtering in the SELECT query, as all the fields are also available for the **WHERE** clause

    ?? Are these conclusions correct?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 12 Functions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The shell provides a list of simple function that operate on a single data column and return a new value. These functions operate on particular types. The shell implements rudimentary type verification and should be able to warn you on incompatible types.

    List of functions, available to be used in the `SELECT` expression can be obtained using the `.help targets` command. List of functions, available to be used in the expression of the `FROM` and `WHERE` clause can be obtained using the `.help from` and `.help where` respectively. E.g.:

    ```text
    beanquery> .help targets


    The list of comma-separated target expressions may consist of columns,
    simple functions and aggregate functions. If you use any aggregate
    function, you must also provide a GROUP-BY clause.

    Columns
    -------
    ...

    Functions
    ---------

    abs(decimal)
    ...

    Aggregate functions
    -------------------

    ...

    sum(amount)
      Calculate the sum of the amount. The result is an Inventory.

    sum(inventory)
      Calculate the sum of the inventories. The result is an Inventory.

    sum(decimal)
    sum(int)
      Calculate the sum of the numerical argument.

    sum(position)
      Calculate the sum of the position. The result is an Inventory.

    ...

    beanquery>
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 12.1 Aggregate functions and Aggregate Queries
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `SELECT` clause (and only the `SELECT clause`) allows usage of the called **Aggregate functions**, in addition to the ordinary Functions.
    The **Aggregate functions** operate on more than a single row. These functions aggregate and summarize the multiple values for the data column that they operate on.

    Examples of aggregate functions include:
    * `COUNT(...)`: Computes the number of postings selected (an integer).
    * `FIRST(...)`, `LAST(...)`: Returns first or last value seen.
    * `MIN(...)`, `MAX(...)`: Computes the minimum or maximum value seen.
    * `SUM(...)`: Sums up the values of each set. This works on amounts, positions, inventories, numbers, etc.

    A usage of at least one of the aggregate function turns a query into the **Aggregate Query**. An **Aggregate query** is a query, which produces a row of results for each group of postings that match the restricts in the `WHERE` clause.  In order to identify the aggregation keys in a **classical SQL** all the non-aggregate columns have to be flagged using the GROUP BY clause:

    Example:
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Assets:Cash USD
    2023-01-01 open Income:Salary USD
    2023-01-01 open Expenses:Food USD
    2023-01-01 open Expenses:Misc USD

    2023-01-01 * "Salary"
      Income:Salary   -500 USD
      Assets:Cash      500 USD

    2023-01-02 * "Alice" "Shopping 1"
      Expenses:Food   10 USD
      Assets:Cash    -10 USD

    2023-01-03 * "Bob" "Shopping 2"
      Expenses:Misc   20 USD
      Assets:Cash    -20 USD

    2023-01-04 * "Alice" "Shopping 3"
      Expenses:Food   30 USD
      Assets:Cash    -30 USD

    2023-01-05 * "Bob" "Shopping 4"
      Expenses:Misc   40 USD
      Assets:Cash    -40 USD

    2023-01-06 * "Alice" "Shopping 5"
      Expenses:Misc   50 USD
      Assets:Cash    -50 USD
    """

    agg_ledger_ui = ledger_editor(_ledger, label="Ledger for aggregate functions demo")
    agg_ledger_ui
    return (agg_ledger_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
        payee, account, sum(position), last(date)
    WHERE 
        account ~ "^Expenses"
    GROUP BY payee, account

    """
    agg_query_ui = query_editor(_sql, label="Aggregate query example")
    agg_query_ui
    return (agg_query_ui,)


@app.cell
def _(agg_ledger_ui, agg_query_ui, query_output):
    query_output(agg_ledger_ui.value, agg_query_ui.value)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
        payee, account, sum(position), last(date)
    WHERE 
        account ~ "^Expenses"
    GROUP BY 1, 2
    """
    agg_query_ui_group_by_position = query_editor(_sql, label="You may also use the positional order of the targets to declare the group key, like this")
    agg_query_ui_group_by_position
    return


@app.cell
def _(agg_ledger_ui, agg_query_ui, query_output):
    query_output(agg_ledger_ui.value, agg_query_ui.value)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
        payee, account as acc, sum(position), last(date)
    WHERE 
        account ~ "^Expenses"
    GROUP BY 1, acc
    """
    agg_query_ui_group_by_position_and_name = query_editor(_sql, label="Furthermore, if you name your targets, you can use the explicit target names:")
    agg_query_ui_group_by_position_and_name
    return (agg_query_ui_group_by_position_and_name,)


@app.cell
def _(agg_ledger_ui, agg_query_ui_group_by_position_and_name, query_output):
    query_output(agg_ledger_ui.value, agg_query_ui_group_by_position_and_name.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Unlike the classical SQL, the beanquery engine however is smart enough to understand what are the grouping keys, without them being explicitly specified. So, it is possible to omit the `GROUP BY` clause at all:
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
        payee, account, sum(position), last(date)
    WHERE 
        account ~ "^Expenses"

    """
    agg_query_without_groupby_ui = query_editor(_sql, label="Aggregate query example")
    agg_query_without_groupby_ui
    return (agg_query_without_groupby_ui,)


@app.cell
def _(agg_ledger_ui, agg_query_without_groupby_ui, query_output):
    query_output(agg_ledger_ui.value, agg_query_without_groupby_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 12.2 Notable functions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This section discusses some of the notable functions, available in beanquery
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 12.2.1 SUM()
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `SUM()` function is probably the most widely used aggregate function in beanquery.

    ```text
    sum(amount)
      Calculate the sum of the amount. The result is an Inventory.

    sum(inventory)
      Calculate the sum of the inventories. The result is an Inventory.

    sum(decimal)
    sum(int)
      Calculate the sum of the numerical argument.

    sum(position)
      Calculate the sum of the position. The result is an Inventory.
    ```
    The usage of the `SUM()` function for a simple case is already demonstrated in the **Aggregate Functions** section.

    Let us apply the `sum()` function to the more complex ledger with lots, tracked at cost and to different commodities.

    Note: for illustrative purposes on the right sit the same ledger is printed using the PRINT query command to show the full internal representation of the lot cost (with the cost date and the cost label. E.g. 1 IVV {10 USD, **2023-01-11}**`)
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Assets:Bank
    2023-01-01 open Income:Salary
    2023-01-01 open Assets:Investment

    2023-01-01 * "Salary"
      Income:Salary   -100000 USD
      Assets:Bank      100000 USD

    2023-01-11 * "Invest in IVV 1"
      Assets:Investment   1  IVV {10 USD} 
      Assets:Bank        -10 USD

    2023-01-12 * "Invest in IVV 2a"
      Assets:Investment   10 IVV {20 USD} 
      Assets:Bank        -200 USD

    2023-01-12 * "Invest in IVV 2b. The same cost as 2a"
      Assets:Investment   20 IVV {20 USD} 
      Assets:Bank        -400 USD

    2023-01-12 * "Invest in IVV 2c. The same cost as 2a, but with label"
      Assets:Investment   40 IVV {20 USD, "lot-label"} 
      Assets:Bank        -800 USD

    2023-01-13 * "Invest in IVV 3. The same cost as 2a, but different date"
      Assets:Investment   100 IVV {20 USD} 
      Assets:Bank        -2000 USD

    2023-01-14 * "Invest in IVV 4. Not at cost with USD"
      Assets:Investment   1000  IVV @ 40 USD 
      Assets:Bank        -40000 USD

    2023-01-15 * "Invest in IPP. Not at cost"
      Assets:Investment   10 IPP @ 4 USD
      Assets:Bank        -40 USD

    """

    sum_with_costs_ledger_ui = ledger_editor(_ledger, label="Ledger for SUM() function demo at costs")
    return (sum_with_costs_ledger_ui,)


@app.cell
def _(mo, query_output, sum_with_costs_ledger_ui):
    # units_costs_ledger_ui
    mo.hstack([sum_with_costs_ledger_ui,
              query_output(sum_with_costs_ledger_ui.value, "PRINT")])
    return


@app.cell
def _(query_editor):
    _sql= """\
    SELECT sum(position)
    WHERE account = "Assets:Investment"
    """

    units_costs_agg_query_ui = query_editor(_sql, label="Aggregate query to sum positions")
    units_costs_agg_query_ui
    return (units_costs_agg_query_ui,)


@app.cell
def _(query_output, sum_with_costs_ledger_ui, units_costs_agg_query_ui):
    query_output(sum_with_costs_ledger_ui.value, units_costs_agg_query_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Observe that:

    * the sum of positions is an inventory<br>
      note, that the way resulting inventory (the sum of positions) is displayed in beanquery may be is a bit confusing, as the cost date cost and label are not displayed (see [this](https://groups.google.com/g/beancount/c/jdNCyhyq3Ug) discussion).
      The more complete representation would be :

    ```text
                sum(position)
    -------------------------------------------
    10   IPP
    1000 IVV
    100  IVV {20 USD, 2023-01-13}
    40   IVV {20 USD, 2023-01-12, "lot-label"}
    30   IVV {20 USD, 2023-01-12}
    1    IVV {10 USD, 2023-01-11}
    ```

    * the `sum()` function joins different lots together, following the rules, which beancount uses to build inventories (see more in the document [How Inventories Work](https://docs.google.com/document/d/11a9bIoNuxpSOth3fmfuIFzlZtpTJbvw-bPaQCnezQJs)):
       * different commodities are not summed together (`10 IPP` and `1000 IVV` are not added together).
       * even when commodities are the same, lots are added together only when all elements of the cost are also the same: the same cost commodity, the same cost date, the same cost label (if available). E.g. in the above example only the following 2 lots are added together:<br> `10 IVV {20 USD, 2023-01-12} + 20 IVV {20 USD, 2023-01-12} = 30 IVV {20 USD, 2023-01-12}`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 12.2.2 UNITS(), COST()
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    cost(position)
      Get the cost of a position.

    cost(inventory)
      Get the cost of an inventory.


    units(position)
      Get the number of units of a position (stripping cost).

    units(inventory)
      Get the number of units of an inventory (stripping cost).
    ```

    Let us see results of these functions on the same ledger, which was used to demonstrate the `SUM()` function.
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT date, narration, account, position, cost(position), units(position)
    WHERE narration ~ "Invest"
    """
    units_costs_query_ui = query_editor(_sql, label="UNITS and COST query")
    units_costs_query_ui
    return (units_costs_query_ui,)


@app.cell
def _(query_output, sum_with_costs_ledger_ui, units_costs_query_ui):
    query_output(sum_with_costs_ledger_ui.value, units_costs_query_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Observe that:

    * the `cost()` function always returns some result, even in case the position is not "held at cost".  In case there is no cost, the cost function returns units.
    * the `cost()` function only returns a cost amount (decimal number and commodity), without the cost date and label

    Both the `cost()` and `units()` functions can operate on positions as well as on inventories. That means, that one can apply these functions either to columns or to the output of the `sum()` function in the aggregate query.  Let us demonstrate this on the same ledger, which was used for the `SUM()` function demo:
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT cost(sum(position)), sum(cost(position)), units(sum(position)),  sum(units(position))
    WHERE account = "Assets:Investment"
    """
    sum_cost_agg_query_ui = query_editor(_sql, label="COST() and UNITS() of inventories")
    sum_cost_agg_query_ui
    return (sum_cost_agg_query_ui,)


@app.cell
def _(query_output, sum_cost_agg_query_ui, sum_with_costs_ledger_ui):
    query_output(sum_with_costs_ledger_ui.value, sum_cost_agg_query_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Observe, that:
    * `cost(sum(position))` produces the same result as the `sum(cost(position))`. In another words, the `cost()` function, does some internal summing. when applied to an inventory. The same is applicable to the `units()`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 12.2.3 CONVERT()
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Beancount offers first-class support for multi-currency accounting. The `CONVERT()` function is a key element of it.

    ```
    convert(amount, str)
    convert(amount, str, date)
      Coerce an amount to a particular currency.

    convert(position, str)
    convert(position, str, date)
      Coerce a position to a particular currency.

    convert(inventory, str)
    convert(inventory, str, date)
      Coerce an inventory to a particular currency.
    ```

    * The first argument is the amount, position, or inventory to be converted.
    * The second argument is the target commodity to convert to.
    * The third (optional) argument is the date at which the exchange rate is looked up. Note that:
      - the function picks the latest price available on or before (but not after) the specified date
      - if the date is omitted, the latest available price is used (?? this may have limited practical financial meaning)

    * Even though not mentioned explicitly, `CONVERT()` internally uses the **prices** table, which is populated by `price` directives. Beanquery hides this complexity from users.
    * Price specifications are reciprocal. In other words, the following two entries are equivalent:
      ```
      2024-01-01 price XXX 2.0 YYY
      ```
      ```
      2024-01-01 price YYY 0.5 XXX
      ```

    In practice, there are several ways to use the `date` parameter:
    * Specify a fixed date (e.g. `2023-01-02`). This is typically used in queries that convert **Assets** and **Liabilities** to a target currency, since under accepted accounting practices these are translated using the exchange rate in effect on the date of the **Net Worth report**.
    * Pass the `date` column as the date parameter. In this case `CONVERT()` uses the posting date to look up the exchange rate, so each posting may use a different rate. This is typically used to convert **Income** and **Expenses**, since under accepted accounting practices these are translated using the exchange rate in effect on the transaction date.
    * Omit the date parameter entirely. In this case `CONVERT()` uses the latest available exchange rate (this may have limited accounting meaning).

    Let us demonstrate this with a simple example:
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\

    2023-01-01 open Assets:Bank 
    2023-01-01 open Expenses:Misc

    2023-01-01 price USD 1 TUG
    2023-01-01 * "Shopping 1 USD" 
        Assets:Bank  -1 USD
        Expenses:Misc 1 USD

    2023-01-02 price USD 10 TUG
    2023-01-02 * "Shopping 2 USD" 
        Assets:Bank  -1 USD
        Expenses:Misc 1 USD

    2023-01-03 price USD 100 TUG
    """

    convert_ledger_ui = ledger_editor(_ledger, label="Ledger for convert function demo")
    convert_ledger_ui
    return (convert_ledger_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT date, narration, account, position, 
           convert(position, "TUG", date) as in_TUG_with_date, 
           convert(position, "TUG", 2023-01-02) as in_TUG_with_fixed_date,
           convert(position, "TUG") as in_TUG_no_date
    WHERE account = "Expenses:Misc"
    """
    convert_query_ui = query_editor(_sql, label="CONVERT() function demo")
    convert_query_ui
    return (convert_query_ui,)


@app.cell
def _(convert_ledger_ui, convert_query_ui, query_output):
    query_output(convert_ledger_ui.value, convert_query_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If no exchange rate is available, `CONVERT()` returns the value in the original currency.

    For example, let us try to convert the previous ledger to EUR.
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT date, narration, account, position, 
           convert(position, "EUR", date) as in_EUR_with_date
    WHERE account = "Expenses:Misc"
    """
    convert_query_not_convert_ui = query_editor(_sql, label="CONVERT() function demo for non-convertible currency")
    convert_query_not_convert_ui
    return (convert_query_not_convert_ui,)


@app.cell
def _(convert_ledger_ui, convert_query_not_convert_ui, query_output):
    query_output(convert_ledger_ui.value, convert_query_not_convert_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    When converting a position that has a cost, `CONVERT()` converts the `UNITS` amount and ignores the cost.

    In the example below, the purchase price is deliberately set differently from the official exchange rate specified by the `price` directive, to illustrate that `CONVERT()` uses only the rate from the `price` directive.
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Assets:Bank
    2023-01-01 open Assets:Investment
    2023-01-01 open Income:Salary


    2023-01-01 * "Salary"
      Income:Salary   -5000 USD
      Assets:Bank      5000 USD

    2023-01-01 price IVV 10 USD
    2023-01-01 * "Investment 1"
      Assets:Investment    1 IVV {15 USD} ; <= purchasing at the price, different from the "official price" (10 USD) on the same day
      Assets:Bank         -15 USD

    2023-01-02 price IPP 100 USD
    2023-01-02 * "Investment 2"
       Assets:Investment    1 IPP {150 USD} ; <= purchasing at the price, different from the "official price" (100 USD) on the same day
       Assets:Bank         -150 USD
      """
    convert_ledger_with_cost_ui = ledger_editor(_ledger, label="Ledger for CONVERT() demo with cost")
    convert_ledger_with_cost_ui
    return (convert_ledger_with_cost_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT date, account, narration, position, convert(position, "USD", 2023-01-31) as position_in_usd
    WHERE account = "Assets:Investment"
    """

    convert_with_cost_query_ui = query_editor(_sql, label="CONVERT() with cost example")
    convert_with_cost_query_ui
    return (convert_with_cost_query_ui,)


@app.cell
def _(convert_ledger_with_cost_ui, convert_with_cost_query_ui, query_output):
    query_output(convert_ledger_with_cost_ui.value, convert_with_cost_query_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For aggregate queries, you can either convert an inventory created by `SUM()`, or sum the results of `CONVERT()`. Note that the former approach is not possible when a different exchange rate must be applied to each posting (i.e., when the `date` column is used instead of a fixed date).
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
         account, 
         convert(sum(position), "USD", 2023-01-31) as total_converted_to_usd,
         sum(convert(position, "USD", 2023-01-31)) as sum_of_converted_to_usd
    WHERE 
         account = "Assets:Investment"
    """
    convert_with_cost_agg_query_ui = query_editor(_sql, label="CONVERT() with cost example for aggregate query")
    convert_with_cost_agg_query_ui
    return (convert_with_cost_agg_query_ui,)


@app.cell
def _(
    convert_ledger_with_cost_ui,
    convert_with_cost_agg_query_ui,
    query_output,
):
    query_output(convert_ledger_with_cost_ui.value, convert_with_cost_agg_query_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 12.2.4 ROOT()
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `ROOT(account_name: str, n: int =1)` function returns the 1st **n** parts from the left of the account name. The default value of the **n** argument is 1.

    E.g. `root("Expenses:Shopping:Misc", 2)` returns `Expenses:Shopping`

    This is very useful to be used together with an aggregate function to consolidate positions together on a higher level of accounts hierarchy.

    E.g.: in the below example we use this function to show P&L -like information, where we show total Income and total Expenses without breaking these down further.
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Assets:Bank
    2023-01-01 open Income:Salary
    2023-01-01 open Income:SideJob
    2023-01-01 open Expenses:Food
    2023-01-01 open Expenses:Misc

    2023-01-01 * "Salary"
      Income:Salary   -1000 USD
      Assets:Bank      1000 USD

    2023-01-02 * "Expenses 1"
      Expenses:Food   100 USD
      Assets:Bank    -100 USD

    2023-01-03 * "Side job"
      Income:SideJob   -200 USD
      Assets:Bank      200 USD

    2023-01-03 * "Expenses 2"
      Expenses:Misc   50 USD
      Assets:Bank    -50 USD
    """

    ledger_root_func_ui = ledger_editor(_ledger, label="Ledger for ROOT() function demo")
    ledger_root_func_ui
    return (ledger_root_func_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
        root(account,1) as acc_shortened,
        sum(position)
    WHERE account ~ "^Expenses|Income"
    """
    root_func_query_ui = query_editor(_sql, label="Using ROOT() function to calculate square")
    root_func_query_ui
    return (root_func_query_ui,)


@app.cell
def _(ledger_root_func_ui, query_output, root_func_query_ui):
    query_output(ledger_root_func_ui.value, root_func_query_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 13 Controlling query results
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 13.1 DISTINCT
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There is a post-filtering phase that supports uniquifying result rows. You can trigger this unique filter with the DISTINCT flag after SELECT, as is common in SQL, e.g.

    _#TODO: add practical examples_
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 13.2 ORDER BY
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Analogous to the GROUP BY clause is an ORDER BY clause that controls the final ordering of the result rows:
    ```
    SELECT …
    GROUP BY account, payee
    ORDER BY payee, date;
    ```
    The clause is optional. If you do not specify it, the default order of iteration of selected postings is used to output the results (that is, the order of transactions-sorted by date- and then their postings).
    As in SQL, you may reverse the order of sorting by a DESC suffix (the default is the same as specifying ASC):
    ```
    SELECT …
    GROUP BY account, payee
    ORDER BY payee, date DESC;
    ```

    _TODO#: add examples_
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 13.3 LIMIT
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The beanquery also supports a LIMIT clause to interrupt output row generation:

    `SELECT … LIMIT 100;`

    This would output the first 100 result rows and then stop. While this is a common clause present in the SQL language, in the context of double-entry bookkeeping it is not very useful: we always have relatively small datasets to work from. Nevertheless, it is provided for completeness.

    _TODO#: add examples_
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 14 Statement operators (OPEN ON, CLOSE ON, CLEAR)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    The shell provides a few operators designed to facilitate the generation of balance sheets and income statements. The particular methodology used to define these operations should be described in detail in the [“introduction to double-entry bookkeeping”](https://docs.google.com/document/d/100tGcA4blh6KSXPRGCZpUlyxaRUwFHEvnz_k9DyZFn4/edit?usp=sharing) document that accompanies Beancount and is mostly located in the source code in the [summarize](https://github.com/beancount/beancount/blob/master/beancount/ops/summarize.py) module.
    These special operators are provided on the FROM clause that is made available on the various forms of query commands in the shell. These further transform the set of entries selected by the FROM expression at the transaction levels (not postings).
    Please note that these are not from standard SQL; these are extensions provided by this shell language only.

    For demonstrations let us use the following ledger (borrowed with some changes from the [summarize_test](https://github.com/beancount/beancount/blob/master/beancount/ops/summarize_test.py))
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2011-01-01 open Income:Salary
    2011-01-01 open Expenses:Taxes
    2011-01-01 open Expenses:Shopping
    2011-01-01 open Liabilities:CreditCard
    2011-01-01 open Assets:US:Checking
    2011-01-01 open Assets:CA:Checking

    2011-03-01 * "Some income and expense to be summarized"
        Income:Salary       -10000 USD
        Expenses:Taxes        3600 USD
        Assets:US:Checking    6400 USD

    2012-03-02 * "Some expenses and liabilities to be summarized"
        Liabilities:CreditCard -200 USD
        Expenses:Shopping       200 USD

    2012-03-03 * "Some conversion to be summarized"
        Assets:US:Checking   -5000 USD @ 1.2 CAD
        Assets:CA:Checking    6000 CAD

    ;; 2012-06-01  BEGIN --------------------------------

    2012-08-01 * "Some income and expense to show"
        Income:Salary       -11000 USD
        Expenses:Taxes        3200 USD
        Assets:US:Checking    7800 USD

    2012-08-02 * "Some other conversion to be summarized"
        Assets:US:Checking   -3000 USD @ 1.25 CAD
        Assets:CA:Checking    3750 CAD

    ;; 2013-01-01  END   --------------------------------

    2013-02-01 * "Some income and expense to be truncated"
        Income:Salary       -10000 USD
        Expenses:Taxes        3600 USD
        Assets:US:Checking    6400 USD
      """

    ledger_ui_open_close = ledger_editor(_ledger, label="Ledger for Statement Operators demo:")
    ledger_ui_open_close
    return (ledger_ui_open_close,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 14.0.1 Opening a Period (OPEN ON clause)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Opening an exercise period at a particular date replaces all entries before that date by summarization entries that book the expected balance against an Equity “opening balances” account and implicitly clears the income and expenses to zero by transferring their balances to an Equity “previous earnings” account (see beancount.ops.summarize.open() for implementation details)
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    PRINT FROM OPEN ON 2012-08-01
    """
    sql_ui_print_open = query_editor(_sql, label="Let us use PRINT statement to demonstrate how OPEN ON converts the ledger")
    # sql_ui_print_open
    return (sql_ui_print_open,)


@app.cell
def _(ledger_ui_open_close, mo, query_output, sql_ui_print_open):
    mo.vstack(
        [
            sql_ui_print_open,
            mo.md("On the left side you see the original ledger for reference and on the right side the ledger transformed by the OPEN ON statement"),
            mo.hstack(
                [ledger_ui_open_close,
                query_output(ledger_ui_open_close.value, sql_ui_print_open.value)
            ]
        )
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    To make it more demonstrative, let's compare balances of accounts on the date before 2012-08-01  without and with OPEN ON 2012-08-01 clause
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
      account, sum(position) as acc_balance

    WHERE 
       date < 2012-08-01
    GROUP BY account
    ORDER BY account
    """
    sql_ui_no_open = query_editor(_sql, label="Without OPEN ON")
    # sql_ui_no_open
    return (sql_ui_no_open,)


@app.cell
def _():
    # query_output(ledger_ui_open_close.value, sql_ui_no_open.value)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
      account, sum(position) as acc_balance
    FROM OPEN ON 2012-08-01
    WHERE 
       date < 2012-08-01
    GROUP BY account
    ORDER BY account
    """
    sql_ui_with_open = query_editor(_sql, label="With OPEN ON")
    # sql_ui_with_open
    return (sql_ui_with_open,)


@app.cell
def _():
    # query_output(ledger_ui_open_close.value, sql_ui_with_open.value)
    return


@app.cell
def _(
    ledger_ui_open_close,
    mo,
    query_output,
    sql_ui_no_open,
    sql_ui_with_open,
):
    mo.hstack(
        [
            mo.vstack(
                [
                    sql_ui_no_open,
                    query_output(ledger_ui_open_close.value, sql_ui_no_open.value)
                ]
            ),
            mo.vstack(
                [
                    sql_ui_with_open,
                    query_output(ledger_ui_open_close.value, sql_ui_with_open.value)
                ]
            )
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    One can see that balances on Assets and Liabilities did not change, but Income and Expenses were summarized into Equity:Earnings:Previous.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 14.0.2 Closing a Period (CLOSE ON clause)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Closing an exercise period involves mainly truncating all entries that come after the given date and ensuring that currency conversions are correctly corrected for (see beancount.ops.summarize.close() for implementation details).

    Note that the closing date should be one day after the last transaction you would like to include (this is in line with the convention we use everywhere in Beancount whereby starting dates are inclusive and ending dates exclusive).
    The closing date is optional. If the date is not specified, the date one day beyond the date of the last entry is used.
    Closing a period leaves the Income and Expenses accounts as they are, that is, their balances are not cleared to zero to Equity. This is because closing is also used to produce final balances for income statements. “Clearing”, as described in the next section, is only needed for balance sheets.
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    PRINT FROM CLOSE ON 2013-01-01
    """
    sql_ui_print_close = query_editor(_sql, label="Let us use PRINT statement to demonstrate how CLOSE ON converts the ledger")
    return (sql_ui_print_close,)


@app.cell
def _(ledger_ui_open_close, mo, query_output, sql_ui_print_close):
    mo.vstack(
        [
            sql_ui_print_close,
            mo.md("On the left side you see the original ledger for reference and on the right side the ledger transformed by the CLOSE ON statement"),
            mo.hstack(
                [ledger_ui_open_close,
                query_output(ledger_ui_open_close.value, sql_ui_print_close.value)
            ]
        )
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    **??** What is this   @ 0 NOTHING. Why is this needed?
    Why is it not possible to put this like this

    ```
    2012-12-31 C "Conversion for (-8000 USD, 9750 CAD)"
      Equity:Conversions:Current   8000 USD @@ 9750 CAD
      Equity:Conversions:Current  -9750 CAD
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 14.0.3 Clearing Income & Expenses (CLEAR clause)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    In order to produce a balance sheet, we need to transfer final balances of the Income and Expenses to an Equity “current earnings” account (sometimes called “retained earnings” or “net income”; you can select the specific account name to use using options in the input file). The resulting balances of income statement accounts should be zero (see beancount.ops.summarize.clear() for implementation details).
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    PRINT FROM CLEAR
    """
    sql_ui_clear = query_editor(_sql, label="Let us use PRINT statement to demonstrate how CLEAR converts the ledger")
    return (sql_ui_clear,)


@app.cell
def _(ledger_ui_open_close, mo, query_output, sql_ui_clear):
    mo.vstack(
        [
            sql_ui_clear,
            mo.md("On the left side you see the original ledger for reference and on the right side the ledger transformed by the CLEAR statement"),
            mo.hstack(
                [ledger_ui_open_close,
                query_output(ledger_ui_open_close.value, sql_ui_clear.value)
            ]
        )
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    To make it more demonstrative, let's compare balances of accounts without and with CLEAR clause
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
      account, sum(position) as acc_balance
    GROUP BY account
    ORDER BY account
    """
    sql_ui_no_clear = query_editor(_sql, label="Without CLEAR")
    return (sql_ui_no_clear,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
      account, sum(position) as acc_balance
    FROM CLEAR
    GROUP BY account
    ORDER BY account
    """
    sql_ui_with_clear = query_editor(_sql, label="With CLEAR")
    return (sql_ui_with_clear,)


@app.cell
def _(
    ledger_ui_open_close,
    mo,
    query_output,
    sql_ui_no_clear,
    sql_ui_with_clear,
):
    mo.hstack(
        [
            mo.vstack(
                [
                    sql_ui_no_clear,
                    query_output(ledger_ui_open_close.value, sql_ui_no_clear.value)
                ]
            ),
            mo.vstack(
                [
                    sql_ui_with_clear,
                    query_output(ledger_ui_open_close.value, sql_ui_with_clear.value)
                ]
            )
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Observe, that the `Equity:Earnings:Current` (by default) contains the net income accumulated during the preceding period. No balances for the Income nor Expenses accounts appear in the output.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 14.0.4 Example Statements
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    The statement operators of course may be combined. For instance, if you wanted to output data for an income statement for year 2012, you could issue the following statement:
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT account, sum(position) 
    FROM OPEN ON 2012-01-01 CLOSE ON 2013-01-01
    WHERE account ~ "Income|Expenses"
    GROUP BY 1
    ORDER BY 1
    """
    sql_ui_income_statement_open_close = query_editor(_sql, label="Income statement example using OPEN ON and CLOSE ON")
    sql_ui_income_statement_open_close 
    return (sql_ui_income_statement_open_close,)


@app.cell
def _(ledger_ui_open_close, query_output, sql_ui_income_statement_open_close):
    query_output(ledger_ui_open_close.value, sql_ui_income_statement_open_close.value)
    return


@app.cell
def _(mo):
    mo.md(r"""
    The same can be achieved by using more traditional WHERE filtering:
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT account, sum(position) 
    WHERE 
         date >= 2012-01-01 and date < 2013-01-01
         AND account ~ "Income|Expenses"
    GROUP BY 1
    ORDER BY 1
    """
    sql_ui_income_statement_where_filter = query_editor(_sql, label="Income statement example using WHERE filter")
    sql_ui_income_statement_where_filter
    return


@app.cell
def _(ledger_ui_open_close, query_output, sql_ui_income_statement_open_close):
    query_output(ledger_ui_open_close.value, sql_ui_income_statement_open_close.value)
    return


@app.cell
def _(mo):
    mo.md(r"""
    To generate a balance sheet, you would add the CLEAR option and select the other accounts:
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT account, sum(position) 
    FROM OPEN ON 2012-01-01 CLOSE ON 2013-01-01 CLEAR
    WHERE not account ~ "Income|Expenses"
    GROUP BY 1
    ORDER BY 1;
    """
    sql_ui_bal_sheet = query_editor(_sql, label="Balance sheet example using OPEN ON, CLOSE ON, CLEAR")
    sql_ui_bal_sheet 
    return (sql_ui_bal_sheet,)


@app.cell
def _(ledger_ui_open_close, query_output, sql_ui_bal_sheet):
    query_output(ledger_ui_open_close.value, sql_ui_bal_sheet.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 15 High-level shortcuts (JOURNAL, BALANCE, PRINT)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    There are two types of queries that are very common for accounting applications: journals and balances reports. This section describes a few additional selection commands that translate directly into SELECT statements and which are then run with the same query code. These are intended as convenient shortcuts.  ?? It looks like the equivalent SELECT statements are more flexible (see more below).

    In this section we will be using the following ledger for all the examples:
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Income:Salary
    2023-01-01 open Assets:Bank-A
    2023-01-01 open Assets:Bank-B
    2023-01-01 open Expenses:Misc 

    2023-01-01 * "Salary"
      Income:Salary   -1000 USD
      Assets:Bank-A    750 USD
      Assets:Bank-B    250 USD

    2023-01-02 * "Shopping using Bank-A"
      Expenses:Misc    100 USD
      Assets:Bank-A   -100 USD

    2023-01-03 * "Shopping using Bank-B"
      Expenses:Misc    110 USD
      Assets:Bank-B   -110 USD

    2023-01-04 * "Shopping using Bank-A again"
      Expenses:Misc    120 USD
      Assets:Bank-A   -120 USD
      """

    ledger_ui_journal = ledger_editor(_ledger, label="Ledger for JOURNAL test")
    ledger_ui_journal
    return (ledger_ui_journal,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 15.1 Selecting Journals (JOURNAL query)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    A common type of query is one that generates a linear journal of entries (Ledger calls this a “register”). This roughly corresponds to an account statement, but with our language, such a statement can be generated for any subset of postings.
    You can generate a journal with the following syntax:

    `JOURNAL <account-regexp> [AT <function>] [FROM …]`

    The regular expression account-regexp is used to select which subset of accounts to generate a journal for. The optional `AT <function>` clause is used to specify an aggregation function for the amounts rendered (typically `UNITS` or `COST`). The `FROM` clause follows the same rules as for the `SELECT` statement and is optional.
    Here is an example journal-generating query:
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    JOURNAL "Assets:Bank-A"
    """
    sql_ui_journal = query_editor(_sql, label="JOURNAL query")
    sql_ui_journal
    return (sql_ui_journal,)


@app.cell
def _(ledger_ui_journal, query_output, sql_ui_journal):
    query_output(ledger_ui_journal.value, sql_ui_journal.value)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT date, narration, account, position, balance
    WHERE account ~ "Assets:Bank-A"
    """
    sql_ui_journal_balance = query_editor(_sql, label="Equivalent to JOURNAL SELECT ... WHERE query")
    sql_ui_journal_balance
    return (sql_ui_journal_balance,)


@app.cell
def _(ledger_ui_journal, query_output, sql_ui_journal_balance):
    query_output(ledger_ui_journal.value, sql_ui_journal_balance.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 15.2 Selecting Balances (BALANCES query)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The other most common type of report is a table of the balances of various accounts at a particular date. This can be viewed as a SELECT query aggregating positions grouping by account.
    You can generate a balances report with the following syntax:

    `BALANCES [AT <function>] [FROM …]`

    The optional `AT <function>` clause is used to specify an aggregation function for the balances rendered (usually UNITS or COST). The `FROM` clause follows the same rules as for the SELECT statement and is optional.
    To generate your balances at a particular date, close your set of entries using the `FROM… CLOSE ON` form described above.

    Observe that typical balance sheets and income statements seen in an accounting context are subsets of tables of balances such as reported by this query. An income statement reports on just the transactions that appears during a period of time, and a balance sheet summarizes transactions before its reporting before and clears the income & expenses accumulated during the period to an equity account. Then some minor reformatting is carried out. Please consult the introduction document on double-entry bookkeeping for more details, and the section above that discusses the “open”, “close” and “clear” operations.
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    BALANCES 
    FROM DATE <=2023-01-03 
    """
    sql_ui_balances = query_editor(_sql, label="BALANCES query")
    # sql_ui_balances
    return (sql_ui_balances,)


@app.cell
def _():
    # query_output(ledger_ui_journal.value, sql_ui_balances.value)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT account, SUM(position)
    WHERE date <=2023-01-03 
    """
    sql_ui_balances_where = query_editor(_sql, label="Equivalent to BALANCES SELECT ... WHERE query")
    # sql_ui_balances_where
    return (sql_ui_balances_where,)


@app.cell
def _():
    # query_output(ledger_ui_journal.value, sql_ui_balances_where.value)
    return


@app.cell
def _(
    ledger_ui_journal,
    mo,
    query_output,
    sql_ui_balances,
    sql_ui_balances_where,
):
    mo.vstack([
        mo.hstack([
            mo.vstack([
                sql_ui_balances,
                query_output(ledger_ui_journal.value, sql_ui_balances.value)
            ]),
            mo.vstack([
                sql_ui_balances_where,
                query_output(ledger_ui_journal.value, sql_ui_balances_where.value)
            ])
        ])
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ?? Seems that the SELECT ... WHERE  offers the same functionality, but with a better flexibility. E.g. it is also possible to filter spesific accounts, and / or apply the root() function to accounts.

    E.g.: would it be possible to do the following with the BALANCES query, where we select balances only for assets?
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT root(account,1) as account_short, SUM(position)
    WHERE date <=2023-01-03 AND account ~ "^Assets"
    """
    sql_ui_balances_where_per_account = query_editor(_sql, label="Balances per set of accounts with WHERE filter")
    sql_ui_balances_where_per_account
    return (sql_ui_balances_where_per_account,)


@app.cell
def _(ledger_ui_journal, query_output, sql_ui_balances_where_per_account):
    query_output(ledger_ui_journal.value, sql_ui_balances_where_per_account.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 15.3 Print (PRINT query)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It can be useful to generate output in Beancount format, so that subsets of transactions can be saved to files, for example. The shell provides that ability via the PRINT command:

    `
    PRINT [FROM …]
    `

    The FROM clause obeys the usual semantics as described elsewhere in this document. The resulting filtered stream of Beancount entries is then printed out on the output in Beancount syntax.
    In particular, just running the `PRINT` command will spit out the parsed and loaded contents of a Beancount file. You can use this for troubleshooting if needed, or to expand transactions generated from a plugin you may be in the process of developing.

    Example:
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    PRINT FROM date >=2023-01-02 
    """
    sql_ui_print = query_editor(_sql, label="Print entries from a specific date")
    sql_ui_print
    return (sql_ui_print,)


@app.cell
def _(ledger_ui_journal, query_output, sql_ui_print):
    query_output(ledger_ui_journal.value, sql_ui_print.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note, that unlike any other type of query commands, the `PRINT` does not produce a tabular data, but just a text output.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 16 Usage of beanquery with Data Frames
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    _#TODO: add information_
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 17 Working around beanquery limitations
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This section will discuss of the beanquery limitations and how to work around them

    _#TODO: add information_

    ### 17.1 No PIVOT functionality

    * Use dataframes

    ### 17.2 No table joining

    * Use built in functions
    * Use data frames
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 18 Example queries for typical situations
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This section collects example of queries to be used in different practical situations

    _#TODO: don't by shy to add lots  of examples_
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 18.1 Net Worth and P&L-like reports in multi-commodities ledger
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One of the typical situations is when some (or all) of Income and  Expenses are done in one currency, but reporting has to be done in another currency. Throughout the accounting period one currency fluctuates against another currency.

    E.g.: let us look at the situation when Income and Expenses are in one currency (TUG), but reporting has to be done in USD. Throughout the accounting period the value of TUG drops from 1 USD to 0.25 USD.
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2023-01-01 open Assets:Bank-A 
    2023-01-01 open Income:Salary
    2023-01-01 open Expenses:Misc

    ; January
    2023-01-01 price USD 1 TUG

    2023-01-01 * "Salary January 2023"
      Assets:Bank-A  2000 TUG
      Income:Salary -2000 TUG

    2023-01-02 * "Expenses January 2023"
      Assets:Bank-A  -1000 TUG
      Expenses:Misc   1000 TUG

    ; June
    2023-06-01 price USD 2 TUG    ; <= big inflation of TUG vs USD

    2023-06-01 * "Salary June 2023"
      Assets:Bank-A  2000 TUG
      Income:Salary -2000 TUG

    2023-06-02 * "Expenses June 2023"
      Assets:Bank-A  -1000 TUG
      Expenses:Misc   1000 TUG

    ; October
    2023-10-01 price USD 4 TUG    ; <= big inflation of TUG vs USD again

    2023-10-01 * "Salary October 2023"
      Assets:Bank-A  2000 TUG
      Income:Salary -2000 TUG

    2023-10-02 * "Expenses October 2023"
      Assets:Bank-A  -1000 TUG
      Expenses:Misc   1000 TUG
    """

    ledger_ui_multi_commodity = ledger_editor(_ledger, label="Multi-commodity ledger")
    ledger_ui_multi_commodity
    return (ledger_ui_multi_commodity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note that, following accepted accounting practices, **Assets** and **Liabilities** are translated into the reporting currency using the exchange rate in effect on the date of the **Net Worth report**. For instance, to determine the current value of your bitcoins, you need to know only your current bitcoin holdings and the current bitcoin price, not the various exchange rates at which you bought them in the past.

    So, broken by accounts the Net-Worth-like report for Y2023 could look like this (for illustration purpose let us also add a column in the original currency):
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
          root(account,1) as account_short, convert(sum(position), "USD", 2023-12-13) as value_conv, sum(position) as value_orig
    WHERE 
           date <= 2023-12-31 AND date >= 2023-01-01 AND account ~ "Assets|Liabilities"
    """
    sql_ui_net_worth_multi_commodity = query_editor(_sql, label="Multi commodity Net Worth query")
    sql_ui_net_worth_multi_commodity
    return (sql_ui_net_worth_multi_commodity,)


@app.cell
def _(
    ledger_ui_multi_commodity,
    query_output,
    sql_ui_net_worth_multi_commodity,
):
    query_output(ledger_ui_multi_commodity.value, sql_ui_net_worth_multi_commodity.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For P&L -like report, inline with accepted accounting practices  **Income**, **Expenses**, and **Liabilities** are translated into the reporting currency using the exchange rate in effect on the transaction date (in contrast to the Net Worth report, which uses the exchange rate on the report date).
    Thus, for example, if you purchased an item for 60 Turkish lira while on vacation in Turkey when 60 lira equaled 2 USD, it will remain 2 USD in the P&L report, regardless of subsequent exchange rate fluctuations.

    So, the P&L -like report could look like this (for illustration purpose let us also add a column in the original currency):
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
          root(account,1) as account_short, 
          sum(convert(position, "USD", date)) as value_conv, 
          sum(position) as value_orig
    WHERE 
           date <= 2023-12-31 
           AND date >= 2023-01-01 
           AND account ~ "Income|Expenses"
    """
    sql_ui_Pand_L_multi_commodity_per_account = query_editor(_sql, label="Multi commodity P&L query by account")
    # sql_ui_Pand_L_multi_commodity_per_account
    return (sql_ui_Pand_L_multi_commodity_per_account,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT 
           sum(convert(position, "USD", date)) as value_conv, 
           sum(position) as value_orig
    WHERE 
           date <= 2023-12-31 
           AND date >= 2023-01-01 
           AND account ~ "Income|Expenses"
    """
    sql_ui_Pand_L_multi_commodity_total = query_editor(_sql, label="Multi commodity P&L query total")
    # sql_ui_Pand_L_multi_commodity_total
    return (sql_ui_Pand_L_multi_commodity_total,)


@app.cell
def _():
    # query_output(ledger_ui_multi_commodity.value, sql_ui_Pand_L_multi_commodity_per_account.value)
    return


@app.cell
def _(
    ledger_ui_multi_commodity,
    mo,
    query_output,
    sql_ui_Pand_L_multi_commodity_per_account,
    sql_ui_Pand_L_multi_commodity_total,
):
    mo.hstack([
        mo.vstack([
            sql_ui_Pand_L_multi_commodity_per_account,
            query_output(ledger_ui_multi_commodity.value, sql_ui_Pand_L_multi_commodity_per_account.value)
        ]),
        mo.vstack([
            sql_ui_Pand_L_multi_commodity_total,
            query_output(ledger_ui_multi_commodity.value, sql_ui_Pand_L_multi_commodity_total.value)
        ])
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Observe, that in this case the P&L report (1750 USD) does not explain the change in the Net Worth in Y2023 (0 USD => 750 USD). However the P&L in TUG (3000 TUG) does explain the change in the Net Worth (3000 TUG).

    This is expected and is happening, because the value of TUG was constantly dropping throughout the year against USD.
    To be able to do the Net Worth reconciliation in the reporting currency (USD in this case) one has to take into account unrealized gains / losses due exchange rate changes (e.g. using the [sing_curr_conv](https://github.com/Ev2geny/evbeantools/blob/main/docs/sing_curr_conv.md) tool).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Simple journal ledger of expense transactions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To get a simple journal of expense postings within a particular date range, one can execute the following:
    """)
    return


@app.cell(hide_code=True)
def _(query_editor):
    _sql = """
    SELECT
        date, flag, description, position, account, other_accounts
    FROM
        account~'Expenses:'
    WHERE
        date >= 2026-01-01
        AND date < 2026-04-01
    """
    sql_ui_simple_journal_ledger_example = query_editor(_sql, "Expense postings in 2026 up to March 31")
    sql_ui_simple_journal_ledger_example
    return (sql_ui_simple_journal_ledger_example,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A couple of things to note:

    * The `description` field conveniently combines the `payee` and `narration` fields, split by a space-padded pipe ' | '
    * `other_accounts` gives the accounts from the other postings on the parent transaction, similarly split by ' | '
        * In this particular example, the other accounts would typically be the payment methods used
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here is an example of the usage of this query on a ledger with a few ordinary expenses:
    """)
    return


@app.cell
def _(ledger_editor):
    _ledger = """\
    2024-01-01 open Liabilities:Some-Card                 USD
    2024-01-01 open Expenses:Car:Repair-and-Maintenance   USD
    2024-01-01 open Liabilities:Some-Other-Card           USD
    2024-01-01 open Expenses:Medical-Expenses             USD
    2024-01-01 open Assets:Checking-Account               USD
    2024-01-01 open Expenses:Clothes-etc                  USD

    2026-03-10 * "Advance Auto Parts" "Synthetic oil and brake fluid"
        Liabilities:Some-Card                -20.84 USD
        Expenses:Car:Repair-and-Maintenance   20.84 USD

    2026-02-15 * "CVS" "Prescription pickup"
        Liabilities:Some-Other-Card   -15.00 USD
        Expenses:Medical-Expenses      15.00 USD

    2026-01-15 * "Target" "Earrings"
        Assets:Checking-Account -78 USD  ; debit card
        Expenses:Clothes-etc
    """

    ledger_ui_simple_txn_list = ledger_editor(_ledger, label='Simple expense transactions')
    ledger_ui_simple_txn_list
    return (ledger_ui_simple_txn_list,)


@app.cell
def _(
    ledger_ui_simple_txn_list,
    query_output,
    sql_ui_simple_journal_ledger_example,
):
    query_output(ledger_ui_simple_txn_list.value, sql_ui_simple_journal_ledger_example.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 19 Appendixes
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 19.1 Appendix A. Shell variables.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The interactive shell has a few “set” variables that you can customize to change some of the behavior of the shell. These are like environment variables. Type the `.set` command to see the list of available variables and their current value.

    The variables are:

    * boxed (boolean): Whether we should draw a box around the output table.
    * expand (boolean): If true, expand columns that render to lists on multiple rows.
    * format (string): The output format. Supported formats: “text”, "csv".
    * narrow (boolean): Whether the column header names are truncated to fit within the display width.
    * nullvalue: '' ?? what does it do?
    * numberify: (boolean): If set to `true` splits columns that contain monetary types (Amount, Position, Inventory) into separate plain-number columns — one per currency found in that column.
    * pager (string): The name of the pager program to pipe multi-page output to when the output is larger than the screen. The initial value is copied from the PAGER environment variable.
    * spaced (boolean): Whether to insert an empty line between every result row. This is only relevant because postings with multiple lots may require multiple lines to be rendered, and inserting an empty line helps delineate those as separate.
    * unicode: (boolean): ?? what does it do?

    To change a variable from its default value, type `.set <variable-name> <new-value>`. E.g.:

    `.set numberify true`
    """)
    return


if __name__ == "__main__":
    app.run()
