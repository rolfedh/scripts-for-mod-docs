# 📄 AsciiDoc Mod Docs Fixer

A set of Python scripts for automatically correcting common issues in modular AsciiDoc files used in Red Hat-style documentation. These tools help prepare content for migration and standardization by enforcing rules from the "Modular documentation templates checklist."

---

## ✅ What the Scripts Fix

There are three scripts in this toolchain. Run them in sequence for best results.

---

### `fix_any_file.py`

Scans all `.adoc` files in a specified directory and applies general fixes or flags issues in any modular documentation file (assemblies, concepts, procedures, or references).

#### Fixes and flags the following:

- **Missing `:_mod-docs-content-type:` declaration**  
  - If the file name starts with a known prefix (`proc_`, `con_`, `ref_`, or `assembly_`), the type is inferred and inserted.
  - If no prefix is found, the script looks for an existing declaration in the file.
  - If no declaration is found, it inserts:
    ```asciidoc
    // TODO: Set the :_mod-docs-content-type: attribute and value
    :_mod-docs-content-type: TBD
    ```

- **Missing topic ID**  
  Adds `[id="filename_{context}"]` at the top of the file.

- **Multiple level-0 (`= `) titles**  
  Adds a `// TODO` comment after the second title to flag the issue.

- **Missing blank line after the level-0 title**  
  Automatically inserts a blank line.

- **Missing short introduction**  
  Adds a `// TODO` comment to prompt the author.

- **Images without alt text**  
  Adds a `// TODO` comment below each `image::[]` with no alt text.

- **Unquoted alt text**  
  Automatically wraps alt text in double quotes.

---

### `fix_assembly_files.py`

After completing your general file fixes and manual cleanup, run this script to enforce structural standards specific to **assembly** files.

#### Fixes and flags the following in assemblies:

- **Missing top-level conditional**  
  Inserts:
  ```asciidoc
  ifdef::context[:parent-context: {context}]
  ```

* **Missing bottom conditionals**
  Appends:

  ```asciidoc
  ifdef::parent-context[:context: {parent-context}]
  ifndef::parent-context[:!context:]
  ```

* **Missing `:context:` declaration**
  Flags the issue with a `// TODO: set a :context: attribute`.

* **Missing blank lines between `include::` statements**
  Inserts blank lines to separate adjacent includes.

* **Illegal section titles**
  Flags `===` or deeper level headings that are not part of an admonition block.

* **Presence of block titles (e.g., `.Note`, `.Procedure`)**
  Flags them with:

  ```asciidoc
  // TODO: Replace the following block title with a `== <subheading>`.
  ```

---

### `fix_concept_reference_files.py`

Run this script after fixing general issues. It flags instructional or structural issues that are specific to **CONCEPT** and **REFERENCE** modules.

#### Flags the following:

- **Imperative instructions in paragraphs or list items**
  - Example: `. Click the button.` or `1. Configure the server.`  
  - Adds a `// TODO: Avoid instructions in concept and reference modules.` comment.

- **Procedural patterns**
  - Flags `.Procedure` and `.Prerequisites` blocks.
  - Flags numbered steps that start with a capital imperative verb.
  - Adds a `// TODO: Consider changing the :_mod-docs-content-type: to PROCEDURE...` comment.

- **Level 2 or deeper section titles (`===` or more)**
  - Flags these unless they are part of an admonition (`====` block).

- **Unexpected block titles**
  - Accepts only `.Next steps` and `.Additional resources`.
  - Flags all others (e.g., `.Note`, `.Procedure`, `.Examples`) unless followed by a structural block (like a table, code block, etc.).

---

### `fix_procedure_files.py`

Run this script after fixing general issues. It enforces structural and content rules specific to **PROCEDURE** modules.

#### Fixes and flags the following in procedures:

- **Operates only on files with `:_mod-docs-content-type: PROCEDURE`**
  - Skips files that do not declare this type.

- **Multiple `.Procedure` block titles**
  - Flags if more than one `.Procedure` block is present.
  - Adds a `// TODO: Must include only one \`.Procedure\` block title and list.` comment.

- **Embellished `.Procedure` block titles**
  - Flags `.Procedure` titles with extra words (e.g., `.Procedure for...`).
  - Adds a `// TODO: The .Procedure block title must not contain additional words.` comment.

- **Missing list after `.Procedure`**
  - Flags if the `.Procedure` block is not immediately followed by an ordered or unordered list.
  - Allows blank lines and comments between `.Procedure` and the list.
  - Adds a `// TODO: Must include a \`.Procedure\` block title followed by an ordered or unordered list.` comment.

- **Content after the last procedure step**
  - Only allows certain block titles after the procedure steps: `.Verification`, `.Troubleshooting`, `.Troubleshooting steps`, `.Next steps`, `.Next step`, `.Additional resources`.
  - Flags any other block titles or content after the last step.
  - Adds a `// TODO: Only \`.Procedure\`, \`.Verification\`, \`.Troubleshooting\`, \`.Next steps\`, etc. are allowed block titles in procedure modules.` comment.
  - Adds a `// TODO: Content found after last procedure step. Only allowed sections may follow.` comment for other content.

- **Special handling for `.Additional resources`**
  - Ensures `.Additional resources` is immediately preceded by `[role="_additional-resources"]`.
  - If missing, inserts `[role="_additional-resources"]` above `.Additional resources`.

- **Never flags content inside code blocks**
  - Skips all flagging logic for lines inside AsciiDoc code blocks (delimited by `----` or `....`).

---

## ⚙️ Prerequisites

* Python 3.x
* No external packages required (uses only the standard library)

---

## 🚀 How to Use

### 1. Clone this repository

```bash
cd ~
git clone https://github.com/rolfedh/scripts-for-mod-docs.git
```

### 2. Create a working branch in your documentation repository

Always run the script on a dedicated branch:

```bash
cd ~/<your_doc_repo_name>
git checkout main
git pull
git checkout -b <your_working_branch_name>
```

---

### 3. Step-by-step usage

#### Step 1: Run `fix_any_file.py` (general issues)

```bash
python ~/scripts-for-mod-docs/fix_any_file.py ./<directory>
```

Or use dry-run mode:

```bash
python ~/scripts-for-mod-docs/fix_any_file.py ./<directory> --dry-run
```

> ✅ After running: Review changes, resolve all `// TODO` items, and verify your changes before continuing.

---

#### Step 2: Run `fix_assembly_files.py` (assembly structure)

```bash
python ~/scripts-for-mod-docs/fix_assembly_files.py ./<path-to-assemblies>
```

Or in dry-run mode:

```bash
python ~/scripts-for-mod-docs/fix_assembly_files.py ./<path-to-assemblies> --dry-run
```

---

#### Step 3: Run `fix_concept_reference_files.py` (concept/reference structural cleanup)

```bash
python ~/scripts-for-mod-docs/fix_concept_reference_files.py ./<path-to-modules>
```

Or in dry-run mode:

```bash
python ~/scripts-for-mod-docs/fix_concept_reference_files.py ./<path-to-modules> --dry-run
```

---

#### Step 4: Run `fix_procedure_files.py` (procedure module structure and content)

```bash
python ~/scripts-for-mod-docs/fix_procedure_files.py ./<path-to-procedures>
```

Or in dry-run mode:

```bash
python ~/scripts-for-mod-docs/fix_procedure_files.py ./<path-to-procedures> --dry-run
```

---

## 📋 Script Output

Each script prints a summary:

* Files it modified
* Files skipped

Files without standard prefixes are still processed if they contain a `:_mod-docs-content-type:` declaration.

---

## 👥 Contributors

* Originally developed by [Rolfe Dlugy-Hegwer](https://github.com/rdlugyhe) as part of Red Hat's Modular Docs standardization initiative.
* Contributors welcome.
* All content and software in this repository is public domain.
