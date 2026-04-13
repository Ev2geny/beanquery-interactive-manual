# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beanquery",
#     "beancount",
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium", css_file="custom.css")


@app.cell(hide_code=True)
def _(heading):
    title_hd = heading(1, "Interactive beanquery manual", number=False)
    title_hd
    return (title_hd,)


@app.cell
def _(mo):
    mo.md("""
 
    """)
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


    def get_beanquery_output(ledger_text: str, query: str) -> str:
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
                render_text(rtypes, rrows, dcontext, buf)

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


    class Heading:
        """A rendered heading with its hierarchical number, used to chain headings in sequence."""
        def __init__(self, html: mo.Html, number: list):
            # pass
            self._html = html
            self.number = number

        def _mime_(self):
            return self._html._mime_()

    def heading(level: int, text: str, prev_heading: Heading | None = None, number: bool = True) -> Heading:
        """Render a colored markdown heading with optional hierarchical numbering.

        Numbering is derived from prev_heading.number, enabling correct ordering
        regardless of marimo cell execution order.

        Args:
            level: Heading level 1-5. Level 1 is reserved for the document title.
            text: Heading text.
            prev_heading: The Heading returned by the preceding heading (not necessarily the immediately preceeding heading)
                          E.g. in the situiation of 1, 1.1, 1.2, 2, the prev_heading for "2" could be either "1" or "1.2" 
                          call in document order. Pass None for the first heading.
            number: If False, no number is generated (e.g. for the document title).
        """
        num = []
        prefix = ""
        if number and 2 <= level <= 5:
            idx = level - 2  # 0=h2, 1=h3, 2=h4, 3=h5
            prev_num = prev_heading.number if prev_heading is not None else []
            parent = prev_num[:idx]
            own = (prev_num[idx] + 1) if len(prev_num) > idx else 1
            num = parent + [own]
            prefix = ".".join(str(n) for n in num) + ". "
        html = mo.md(f"{'#' * level} {prefix}{text}")
        return Heading(html, num)


    return heading, ledger_editor, mo, query_editor, query_output


@app.cell(hide_code=True)
def _(heading, title_hd):
    intro_hd = heading(2, "Introduction to this document", title_hd, number=True)
    intro_hd
    return (intro_hd,)


@app.cell
def _(heading, intro_hd):
    purpose_hd = heading(3, "Purpose and scope", intro_hd, number=True)
    purpose_hd
    return (purpose_hd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is an interactive manual/tutorial for the [beanquery](https://github.com/beancount/beanquery) - a customizable and extensible lightweight SQL query tool for the [Beancount](https://github.com/beancount/beancount/) ledger data.

    The goal is for this document to be a follow up of the beancount v2 [Beancount Query Language](https://docs.google.com/document/d/1s0GOZMcrKKCLlP29MD7kHO4L88evrwWdIO0p4EwRBE0/edit?usp=sharing) document.

    It is created with the following features in mind:

    * to cover latest features of the beanquery
    * to include a lot of actual examples on actual ledgers
    * to be self-documenting for the query outputs (query outputs are computed with actual beanquery as a part of the notebook execution)
    * to be interactive. If it is run as a marimo notebook, then a reader can experiment by changing default ledgers and/or queries to get an updated query outputs.
    """)
    return


@app.cell(hide_code=True)
def _(heading, purpose_hd):
    how_to_use__man_h = heading(3, "How to use this manual", purpose_hd)
    how_to_use__man_h
    return (how_to_use__man_h,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The document assumes no prior knowledge of the SQL language and is structured as much as possible in the form of a tutorial, where each chapter builds on the material covered in the previous ones. As a downside, the material is more scattered throughout the document than it would otherwise be if an SQL-familiar reader would be assumed. E.g. the available tables are introduces in one chapter and then some more detailed information about some of the tables is added in several chapters afterwards.

    This document is written in the [marimo](https://docs.marimo.io/) notebook. You can read the manual as a normal html document.
    However the cool feature of this notebook is that if you run it as a marimo notebook, you can interact with the document by changing the default text for both the ledger and the query in all examples. As soon as an input widget loses focus, the query will be re-executed and the output will be updated.

    Both in the HTML format as well as in the marimo notebook format the clickable table of content is available if one hovers the mouse near the right browser vertical scroll bar.

    Note that throughout the document some unresolved questions the author had about the beanquery functionality are marked with double question marks.

    E.g.: ?? Why do we need this.

    As well as some TODOs, marked with #TODO.

    E.g.: _#TODO: we need to investigate this_
    """)
    return


@app.cell
def _(heading, how_to_use__man_h):
    int_beanquery_hd = heading(2, "Introduction to beanquery", how_to_use__man_h, number=True)
    int_beanquery_hd
    return (int_beanquery_hd,)


@app.cell
def _(mo):
    mo.md(r"""
    Beanquery parses a Beancount ledger and creates an in-memory database represented in a form of several tables. Beanquery then exposes a command-line tool that acts like a client to that in-memory database in which you can type queries in a variant of SQL.

    Beanquery started as an experiment in beancount v2, but in v3 (when **bean-report** and **bean-web** have been discontinued) became practically the only tool to query information out of beancount ledger. Thus one can say, that in v3 beancount has moved towards the [Self-service business intelligence](https://www.techtarget.com/searchbusinessanalytics/definition/self-service-business-intelligence-BI) model instead of providing off the shelf ready to use reports.

    So one might ask: Why create another SQL client? Why not output the data to an SQLite database and allow the user to use that SQL client? Apparently this experiment was conducted by creating the [bean-sql](https://github.com/beancount/beancount/blob/v2/beancount/scripts/sql.py). It appears, that writing queries was painful and carrying out operations on lots that are held at cost was difficult.

    Therefore beanquery has some extras that are essential for querying a Beancount ledger. These extras include (but are not necessarily limited to) the following:
    * The client supports the semantics of inventory booking implemented in Beancount. It also supports aggregation functions on inventory objects and rendering functions (e.g., COST() to render the cost of an inventory instead of its contents).
    * The client supports some functions, which run on postings, but in a background access other tables (e.g. CONVERT() function, which formally operates on the amount, position or inventory, but in a background uses the prices table as well).
    * It allows filtering at two levels simultaneously: you can filter whole transactions, which has the benefit of respecting the accounting equation, and then, usually for presentation purposes, you can also filter at the postings level.
    * Objects in one table already have a reference to related objects in another table. E.g. records in the postings table have a reference to the related object from the transactions table. So one can say that these tables have already been pre-joined (even though technically this is not correct).
    * Transactions can be summarized in a manner useful to produce balance sheets and income statements. For example, our SQL variant explicitly supports a “close” operation with an effect similar to closing the year, which inserts transactions to clear income statement accounts to equity and removes past history.
    """)
    return


@app.cell(hide_code=True)
def _(heading, int_beanquery_hd):
    how_to_install_h = heading(2, "How to install beanquery", int_beanquery_hd)
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
    how_to_run_hd = heading(2, "How to run beanquery CLI", how_to_install_h)
    how_to_run_hd
    return (how_to_run_hd,)


@app.cell
def _(mo):
    mo.md(r"""
    To run beanquery type

    ```shell
    bean-query [OPTIONS] FILENAME [QUERY]...
    ```

    This launches the query tool in interactive mode, where you can enter multiple commands on the dataset loaded in memory. The beanquery parses the input file, spits out a few basic statistics about your ledger, and provides a command prompt for you to enter query commands.

    e.g.:

    ```shell
    bean-query  test.bean
    Input file: "Beancount"
    Ready with 3 directives (2 postings in 1 transactions, 0 validation errors)
    beanquery>
    ```

    If any errors in your ledger are incurred, they are printed before the prompt.

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
    """)
    return


@app.cell
def _(heading, how_to_run_hd):
    shell_variables_hd = heading(2, "Shell variables", how_to_run_hd, number=True)
    shell_variables_hd
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The interactive shell has a few “set” variables that you can customize to change some of the behavior of the shell. These are like environment variables. Type the `.set` command to see the list of available variables and their current value.

    The variables are:

    * boxed (boolean): Whether we should draw a box around the output table.
    * expand (boolean): If true, expand columns that render to lists on multiple rows.
    * format (string): The output format. Supported formats: “text”, "csv".
    * narrow (boolean): Whether the column header names are truncated, underling selected data allows
    * nullvalue: '' ?? what does it do?
    * numberify: (boolean): If set to `true` splits columns that contain monetary types (Amount, Position, Inventory) into separate plain-number columns — one per currency found in that column.
    * pager (string): The name of the pager program to pipe multi-page output to when the output is larger than the screen. The initial value is copied from the PAGER environment variable.
    * spaced (boolean): Whether to insert an empty line between every result row. This is only relevant because postings with multiple lots may require multiple lines to be rendered, and inserting an empty line helps delineate those as separate.
    * unicode: (boolean): ?? what does it do?

    To change the invironmental variable from the default one type `.set <variable-name> <new-value>`. E.g.:

    `.set numberify true`
    """)
    return


@app.cell
def _(heading, how_to_run_hd):
    how_to_get_help_h = heading(2, "How to get help", how_to_run_hd)
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

    To get help on a specific command type `.help <command name>`

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

    e.g. to see list of columns in the **postings** table type

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
    available_tables = heading(2, "Available tables. Introduction", how_to_get_help_h, number=True)
    available_tables
    return (available_tables,)


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

    List of fields in every table can be obtained using the `.describe <table_name>` command

    Note: for the postings table the more complete list of columns can be obtained used the `.help targets` command.
    """)
    return


@app.cell
def _(available_tables, heading):
    types_of_queries_hd = heading(2, "Types of queries", available_tables, number=True)
    types_of_queries_hd
    return (types_of_queries_hd,)


@app.cell
def _(mo):
    mo.md(r"""
    Beanquery supports the following type of queries, further discussed in this document

    * SELECT
    * BALANCES
    * JOURNAL
    * PRINT
    """)
    return


@app.cell
def _(heading, types_of_queries_hd):
    select_query_hd = heading(2, "SELECT Query", types_of_queries_hd, number=True)
    select_query_hd
    return (select_query_hd,)


@app.cell
def _(mo):
    mo.md(r"""
    The beanquery SELECT query loosely follows the standard SQL query with some deviations, which will be discussed throughout this manual

    It has to be noted, that originally **beanquery** was designed to be used to extract information on postings table only. In this situation the **FROM** part of the SQL query was "hijacked" to be used for transaction-level filtering and **WHERE** was used for posting-level filtering, which introduced so-called  two-level filtering syntax

    So, the SELECT query structure looked like this (written in the informal EBNF language):

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

    Later on, in beancount v3, when beanquery was moved to be a standalone tool, it was extended to query more tables (see above). In this situation the FROM part was needed again to select a table, so a new form of the SELECT query was introduced:

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
    * The **#table** form allows querying tables other than the postings table, but when it is used to query the postings table (which is possible), it lacks some functionality available in the traditional form, namely the `[OPEN ON <date>] [CLOSE [ON <date>]] [CLEAR]` part. (This may actually be a [bug](https://github.com/beancount/beanquery/issues/274), rather than a feature).

    So, let us emphasize:
    * In the traditional BQL the FROM clause is used to describe the posting-level filter, not to describe the source of the data
    * In the **#table** syntax the table name has to be preceded by the # symbol
    * In the BQL using a wildcard as the target list (“*”) selects a good default list of columns, whilst the normal SQL the * is used to describe the complete set of columns, available in the table

    At the moment beanquery supports both query types. Let us explore this on a simple ledger
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

    Difference to SQL: the BQL using a wildcard as the target list (“*”) selects a good default list of columns, whilst the traditional SQL the * is used to describe the complete set of columns, available in the table
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Let us query the **accounts** table
    """)
    return


@app.cell
def _(query_editor):
    _sql = """\
    SELECT account, open.date, close.date
    FROM #accounts
    """
    sql_ui_hash_table_accounts = query_editor(_sql, label=r"\# table syntax query on accounts (only \#table style can be used for the accounts table)")
    sql_ui_hash_table_accounts
    return (sql_ui_hash_table_accounts,)


@app.cell
def _(query_output, simple_ledger_ui, sql_ui_hash_table_accounts):
    query_output(simple_ledger_ui.value, sql_ui_hash_table_accounts.value) 
    return


@app.cell
def _(heading, select_query_hd):
    expressions_hd = heading(2, "Expressions", select_query_hd, number=True)
    expressions_hd
    return (expressions_hd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    When we talked about SQL query we mentioned, but not defined the notion of an expression. Let us correct this.

    An **expression** is something, which can be evaluated to a value.

    A **logical expression** is an expression, which can be evaluated to a  logical value (`TRUE` or `FALSE`)

    In beanquery an expression is constructed by combining **table columns**, **constants**, **operators**, and **functions**. All of these elements are described later in this document.
    """)
    return


@app.cell
def _(expressions_hd, heading):
    operators_hd = heading(3, "Operators", expressions_hd, number=True)
    operators_hd
    return (operators_hd,)


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


@app.cell
def _(heading, operators_hd):
    constants_hd = heading(3, "Constants", operators_hd, number=True)
    constants_hd
    return (constants_hd,)


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


@app.cell
def _(constants_hd, heading):
    columns_functions_hd = heading(3, "Columns and Functions in expressions", constants_hd, number=True)
    columns_functions_hd
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

    _\#TODO: investigate this and raise an issue, if applicable_
    """)
    return


@app.cell
def _(expressions_hd, heading):
    more_on_tables_hd = heading(2, "More on tables", expressions_hd, number=True)
    more_on_tables_hd
    return (more_on_tables_hd,)


@app.cell
def _(mo):
    mo.md(r"""
    This section contains some additional information on some of the tables, available in beanquery.
    """)
    return


@app.cell
def _(heading, more_on_tables_hd):
    postings_table_hd = heading(3, "The postings table", more_on_tables_hd, number=True)
    postings_table_hd
    return (postings_table_hd,)


@app.cell
def _(mo):
    mo.md(r"""
    As it was already mentioned, the beanquery was originally created to work with the postings table only, therefore the postings table has some notable and sometimes unexpected features
    """)
    return


@app.cell
def _(heading, postings_table_hd):
    transaction_columns_in_postings_hd = heading(4, "Transactions columns in the postings table", postings_table_hd, number=True)
    transaction_columns_in_postings_hd
    return (transaction_columns_in_postings_hd,)


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
    # ledger_ui_post_vs_tr
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


@app.cell
def _(heading, transaction_columns_in_postings_hd):
    hard_coded_joints_postings_transactions = heading(4, "The `entry` column", transaction_columns_in_postings_hd, number=True)
    hard_coded_joints_postings_transactions
    return (hard_coded_joints_postings_transactions,)


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


@app.cell
def _(hard_coded_joints_postings_transactions, heading):
    other_accounts_column_hd = heading(4, "The `other_accounts` column", hard_coded_joints_postings_transactions, number=True)
    other_accounts_column_hd
    return (other_accounts_column_hd,)


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


@app.cell
def _(heading, other_accounts_column_hd):
    balance_column_hd = heading(4, 'The `balance` column', other_accounts_column_hd, number=True)
    balance_column_hd
    return (balance_column_hd,)


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


@app.cell
def _(balance_column_hd, heading):
    weight_hd = heading(4, "The `weight` column", balance_column_hd, number=True)
    weight_hd
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The computed weight used for this posting

    _#TODO: add expamples_
    """)
    return


@app.cell
def _(heading, postings_table_hd):
    transactions_table_hd = heading(3, "Transactions table", postings_table_hd, number=True)
    transactions_table_hd
    return (transactions_table_hd,)


@app.cell
def _(heading, transactions_table_hd):
    id_column_dh = heading(4, "The `id` column", transactions_table_hd, number=True)
    id_column_dh
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


@app.cell
def _(heading, more_on_tables_hd):
    practical_conclusions_select_q_hd = heading(2, "Practical conclusions on using the SELECT Query", more_on_tables_hd, number=True)
    practical_conclusions_select_q_hd
    return (practical_conclusions_select_q_hd,)


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


@app.cell
def _(heading, practical_conclusions_select_q_hd):
    functions_hd = heading(2, "Functions", practical_conclusions_select_q_hd, number=True)
    functions_hd
    return (functions_hd,)


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


@app.cell
def _(functions_hd, heading):
    aggregate_functions_and_q_hd = heading(3, "Aggregate functions and Aggregate Queries", functions_hd, number=True)
    aggregate_functions_and_q_hd
    return (aggregate_functions_and_q_hd,)


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


@app.cell
def _(aggregate_functions_and_q_hd, heading):
    notable_functions_hd = heading(3, "Notable functions", aggregate_functions_and_q_hd, number=True)
    notable_functions_hd
    return (notable_functions_hd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This section discusses some of the notable functions, available in beanquery
    """)
    return


@app.cell
def _(heading, notable_functions_hd):
    units_costs_func_hd = heading(4, "UNITS() and COST() functions", notable_functions_hd, number=True)
    units_costs_func_hd
    return (units_costs_func_hd,)


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

    Let us see results of these functions on a simple ledger
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

    2023-01-11 * "Investment 1"
      Assets:Investment   1  IVV {10 USD} 
      Assets:Bank        -10 USD

    2023-01-12 * "Investment 2"
      Assets:Investment   10 IVV {20 USD} 
      Assets:Bank        -200 USD

    2023-01-13 * "Investment 3. The same cost as Investment 2, but diff date"
      Assets:Investment   100 IVV {20 USD} 
      Assets:Bank        -2000 USD

    2023-01-14 * "Investment 4. Not at cost"
      Assets:Investment   1000  IVV @ 40 USD 
      Assets:Bank        -40000 USD

    """

    units_costs_ledger_ui = ledger_editor(_ledger, label="UNITS and COST example ledger")

    units_costs_ledger_ui
    return (units_costs_ledger_ui,)


@app.cell
def _(query_editor):
    _sql = """\
    SELECT date, account, narration, position, cost(position), units(position)
    WHERE narration ~ "Investment"
    """
    units_costs_query_ui = query_editor(_sql, label="UNITS and COST query")
    units_costs_query_ui
    return (units_costs_query_ui,)


@app.cell
def _(query_output, units_costs_ledger_ui, units_costs_query_ui):
    query_output(units_costs_ledger_ui.value, units_costs_query_ui.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note, that the cost function always returns some result, even in case the position is not "held at cost".  In case there is no cost, the cost function returns units.

    Both the `cost()` and `units()` functions can operate on positions as well as on inventories. That means, that one can apply these functions either to columns or to the output of the `sum()` function in the aggregate query. See the `SUM()` function section to see how these functions work on inventory.
    """)
    return


@app.cell
def _(heading, units_costs_func_hd):
    sum_function_hd = heading(4, "The `SUM()` function", units_costs_func_hd, number=True)
    sum_function_hd
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
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

    Note, that when the `SUM()` is applied to positions, which are held at cots
    """)
    return


@app.cell
def _(query_editor):
    _sql= """\
    SELECT sum(position), sum(cost(position)), sum(units(position)), units(sum(position)), cost(sum(position))
    WHERE account = "Assets:Investment"
    """

    units_costs_agg_query_ui = query_editor(_sql, label="Aggregate query to sum up the total units and costs of the investments")
    units_costs_agg_query_ui

    return (units_costs_agg_query_ui,)


@app.cell
def _(query_output, units_costs_agg_query_ui, units_costs_ledger_ui):
    query_output(units_costs_ledger_ui.value, units_costs_agg_query_ui.value)
    return


@app.cell
def _(functions_hd, heading):
    controlling_results_hd = heading(2, "Controlling query results", functions_hd, number=True)
    controlling_results_hd
    return (controlling_results_hd,)


@app.cell
def _(controlling_results_hd, heading):
    distinct_hd = heading(3, "DISTINCT", controlling_results_hd, number=True)
    distinct_hd
    return (distinct_hd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There is a post-filtering phase that supports uniquifying result rows. You can trigger this unique filter with the DISTINCT flag after SELECT, as is common in SQL, e.g.

    _#TODO: add practical examples_
    """)
    return


@app.cell
def _(distinct_hd, heading):
    order_by_hd = heading(3, "ORDER BY", distinct_hd, number=True)
    order_by_hd
    return (order_by_hd,)


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


@app.cell
def _(heading, order_by_hd):
    limit_hd = heading(3, "LIMIT", order_by_hd, number=True)
    limit_hd
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


@app.cell
def _(controlling_results_hd, heading):
    statement_operators_hd = heading(2, "Statement operators (OPEN ON, CLOSE ON, CLEAR)", controlling_results_hd, number=True)
    statement_operators_hd
    return (statement_operators_hd,)


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


@app.cell
def _(heading, statement_operators_hd):
    openning_period_hd = heading(4, "Opening a Period (OPEN ON clause)", statement_operators_hd, number=True)
    openning_period_hd
    return (openning_period_hd,)


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


@app.cell
def _(heading, openning_period_hd):
    closing_period_hd = heading(4, "Closing a Period (CLOSE ON clause)", openning_period_hd, number=True)
    closing_period_hd
    return (closing_period_hd,)


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


@app.cell
def _(closing_period_hd, heading):
    clearing_period_hd = heading(4, "Clearing Income & Expenses (CLEAR clause)", closing_period_hd, number=True)
    clearing_period_hd
    return (clearing_period_hd,)


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


@app.cell
def _(clearing_period_hd, heading):
    open_close_clear_hd = heading(4, "Example Statements", clearing_period_hd, number=True)
    open_close_clear_hd
    return (open_close_clear_hd,)


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


@app.cell
def _(heading, open_close_clear_hd):
    high_level_shortcuts_hd = heading(2, "High-level shortcuts (JOURNAL, BALANCE, PRINT)", open_close_clear_hd, number=True)
    high_level_shortcuts_hd
    return (high_level_shortcuts_hd,)


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


@app.cell
def _(heading, high_level_shortcuts_hd):
    journal_hd = heading(3, "Selecting Journals (JOURNAL query)", high_level_shortcuts_hd, number=True)
    journal_hd
    return (journal_hd,)


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


@app.cell
def _(heading, journal_hd):
    balances_hd = heading(3, "Selecting Balances (BALANCES query)", journal_hd, number=True)
    balances_hd
    return (balances_hd,)


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


@app.cell
def _(balances_hd, heading):
    print_hd = heading(3, "Print (PRINT query)", balances_hd, number=True)
    print_hd
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


if __name__ == "__main__":
    app.run()
