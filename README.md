# 📄 AsciiDoc Mod Docs Fixer

A Python script for automatically correcting common issues in modular AsciiDoc files used in Red Hat-style documentation. The script helps prepare content for content migration and standardization by enforcing rules from the "Modular documentation templates checklist"

---

## ✅ What the Script Fixes

The script scans all `.adoc` files in a specified directory and applies fixes or flags the following issues:

### For all modules and assemblies:

- **Missing `:_mod-docs-content-type:` declaration**  
  Infers the content type (`PROCEDURE`, `CONCEPT`, `REFERENCE`, or `ASSEMBLY`) from the filename prefix (`proc_`, `con_`, `ref_`, or `assembly_`).

- **Missing topic ID**  
  Inserts an ID in the format `[id="filename_{context}"]` at the top of the file.

- **Multiple level-0 (`= `) titles**  
  Adds a `// TODO` comment after the second title to flag a potential structure issue.

- **Missing blank line after the level-0 title**  
  Inserts a blank line to improve structure and readability.

- **Missing short introduction**  
  Adds a `// TODO` comment prompting the user to insert a short intro paragraph after the title.

- **Images without alt text**  
  Adds a `// TODO` comment below any image line missing alt text.

- **Alt text not enclosed in quotation marks**  
  Automatically wraps alt text in quotation marks.

---

## ⚙️ Prerequisites

- Python 3.x  
- No external packages required (uses only the standard library)

---

## 🚀 How to Use

### 1. Clone this repository

```bash
cd ~
git clone https://github.com/rolfedh/scripts-for-mod-docs.git
````

### 2. Create a working branch in your documentation repository

Running the script modifies files. Always work in a dedicated feature or fix branch.

```bash
git checkout main
git pull
git checkout -b fix-modules
```

### 3. Run the script from the root of your module directory

```bash
python ~/scripts-for-mod-docs/asciidoc_fix_tool.py ./path/to/modules
```

### Optional: Dry-run mode (no changes written to disk)

```bash
python ~/scripts-for-mod-docs/asciidoc_fix_tool.py --dry-run
```

This mode shows what the script *would* fix without making changes.

### Optional: Find and fix issues flagged as `// TODO` before merging changes

```bash
python ~/scripts-for-mod-docs/asciidoc_fix_tool.py --dry-run
```
---

## 📋 Script Output

After running, the script prints a summary of:

* Files it modified
* Files it skipped (e.g., non-AsciiDoc files or unrecognized types)

---

## 👥 Contributors

Originally developed by [Rolfe Dlugy-Hegwer](https://github.com/rdlugyhe) as part of the Modular Docs standardization initiative.
