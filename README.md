# Interactive beanquery manual

This is an interactive manual and tutorial for [beanquery](https://github.com/beancount/beanquery) — a customizable, extensible, lightweight SQL-like query tool for [Beancount](https://github.com/beancount/beancount/) ledger data.

This document is intended as a follow-up to the Beancount v2 [Beancount Query Language](https://docs.google.com/document/d/1s0GOZMcrKKCLlP29MD7kHO4L88evrwWdIO0p4EwRBE0/edit?usp=sharing) document.

It was created with the following goals in mind:

* to cover the latest features of beanquery
* to include many real examples using actual ledgers
* to be self-documenting: all query outputs are computed by running beanquery as part of the notebook execution
* to be interactive: when run as a [marimo](https://marimo.io/) notebook, readers can experiment by changing the default ledgers and/or queries, with outputs updating automatically

**Current state**: work is ongoing. 
Comments, feedback and PRs are more than welcome!

## 1 How to open the manual

### 1.1 As a static HTML file

As a static HTML file the manual can be read at the **[GitHub Pages](https://ev2geny.github.io/beanquery-interactive-manual/)**

### 1.2 To interact with the document, whilst reading

#### 1.2.1 Option 1: From the Marimo [Molab](https://molab.marimo.io/) cloud

1. Click on [this](https://molab.marimo.io/github.com/Ev2geny/beanquery-interactive-manual/manual.py) URL
   
2. Once the notebook is open in the Molab cloud, click Login button on the right side. If needed, create an account.
   
3. Click on the Fork button on the top right
   
   ![fork_image](images/fork.png)

4. Once the notebook has been forked, click on the Run button on the bottom right.
   
   ![marimo run](images/marimo_run.png)

5. Wait for notebook to run (the Run button will change its color to white)
6. Click on the **Toggle app view** button to display the notebook in the view mode (to hide the code).

![Toogle app view](images/toggle_app_view.png)

#### 1.2.2 Option 2: Locally on your PC

To be able to interact with the manual (to change queries, ledgers) one has to run it as a marimo notebook.
To achieve this do the following:

1. If not done yet, install uv for your OS, following the [official instructions](https://docs.astral.sh/uv/getting-started/installation/)
   
2. Clone this directory:
   ```
   git clone https://github.com/Ev2geny/beanquery-interactive-manual.git

   cd beanquery-interactive-manual
   ```
3. Run the notebook in the view only mode:
   ```
   uv run marimo run manual.py
   ```

## 2 How to read the manual

Use the popping Table of Content on the right side to navigate the document

![toc](images/TOC.png)
