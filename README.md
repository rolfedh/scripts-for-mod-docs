# 📄 AsciiDoc Modular Docs Fixer

This Python script automatically audits and corrects common structural and formatting issues in modular AsciiDoc files used in Red Hat-style documentation. It supports content migration readiness by enforcing rules defined in the [Modular Documentation Templates Checklist](https://github.com/redhat-documentation/modular-docs/).

---

## ✅ What It Does

The script scans all `.adoc` files in a directory and applies fixes or flags the following issues:

### All modules and assemblies:

* **Missing `:_mod-docs-content-type:` declaration**
  → Infers the type (`PROCEDURE`, `CONCEPT`, `REFERENCE`, or `ASSEMBLY`) from the filename prefix.
* **Missing topic ID**
  → Inserts `[id="filename_{context}"]` at the top of the file.
* **Multiple level 0 (`= `) titles**
  → Flags with a `// TODO` comment after the second title.
* **Missing blank line after level 0 title**
  → Inserts a blank line for structural clarity.
* **Missing short introduction**
  → Flags with a `// TODO` comment prompting the user to add a short paragraph after the title.
* **Images without alt text**
  → Adds a `// TODO` comment below image lines that have no alt text.
* **Alt text without quotation marks**
  → Automatically wraps the description in quotes.

---

## 🚀 How to Use

### 1. Install Python (3.x)

No additional packages are required — the script uses only the standard library.

### 2. Run the script

```bash
python asciidoc_fix_tool.py ./path/to/modules
```

### Optional: Dry-run mode (no files modified)

```bash
python asciidoc_fix_tool.py ./path/to/modules --dry-run
```

This will print what would be fixed, but leave files unchanged.

---

## 📝 Output

The script prints a summary of:

* Files it fixed
* Files it skipped (e.g., unknown type or non-AsciiDoc)

---

## ⚠️ Notes

* This script uses filename prefixes like `proc_`, `con_`, `ref_`, and `assembly_` to infer document types.
* Fixes are made **in place**. You may want to back up your `.adoc` files or version them in Git before running.

---

## 👥 Contributors

Originally developed by [Rolfe Dlugy-Hegwer](https://github.com/rdlugyhe) as part of Modular Docs standardization efforts.
