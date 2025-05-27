import os
import re
import argparse

# ------------------------
# Regex patterns for common structural issues
# ------------------------
include_pattern = re.compile(r'^include::')
h2_title_pattern = re.compile(r'^(===+)\s+\S')  # Matches headings with at least three = followed by text
block_title_pattern = re.compile(r'^\.[A-Za-z].*')
context_declaration_pattern = re.compile(r'^:context:')
assembly_type_pattern = re.compile(r':_mod-docs-content-type:\s*ASSEMBLY')

# ------------------------
# Ensure the top-level conditional is present
# ------------------------
def ensure_top_conditional(lines):
    expected = "ifdef::context[:parent-context: {context}]\n"
    if expected not in lines[:10]:
        lines.insert(0, expected)
        return True
    return False

# ------------------------
# Ensure the bottom conditional block is present
# ------------------------
def ensure_bottom_conditionals(lines):
    expected_1 = "ifdef::parent-context[:context: {parent-context}]\n"
    expected_2 = "ifndef::parent-context[:!context:]\n"
    tail = lines[-5:]
    if expected_1 not in tail or expected_2 not in tail:
        lines.append("\n")
        lines.append(expected_1)
        lines.append(expected_2)
        return True
    return False

# ------------------------
# Ensure the file has a :context: declaration
# ------------------------
def ensure_context_variable(lines):
    for line in lines:
        if context_declaration_pattern.match(line.strip()):
            return False
    lines.insert(0, "// TODO: set a :context: attribute\n")
    return True

# ------------------------
# Ensure blank lines between each include:: statement
# ------------------------
def ensure_include_spacing(lines):
    i = 0
    changed = False
    while i < len(lines) - 1:
        if include_pattern.match(lines[i].strip()) and include_pattern.match(lines[i + 1].strip()):
            lines.insert(i + 1, "\n")
            changed = True
            i += 1
        i += 1
    return changed

# ------------------------
# Flag invalid level 2 or deeper titles (ignore '====' with no title text)
# ------------------------
def flag_illegal_headings(lines):
    changed = False
    for idx, line in enumerate(lines):
        if line.strip().startswith("===") and line.strip() != "====":
            lines.insert(idx, "// TODO: Remove or revise level 2+ heading\n")
            changed = True
            break
    return changed

# ------------------------
# Flag block titles (e.g., .Note, .Procedure)
# ------------------------
def flag_block_titles(lines):
    for idx, line in enumerate(lines):
        if block_title_pattern.match(line.strip()):
            lines.insert(idx, "// TODO: Replace the following block title with a `== <subheading>`.\n")
            return True
    return False

# ------------------------
# Apply all fixes to a single file
# ------------------------
def fix_assembly_file(filepath, dry_run=False):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Only operate on files with :_mod-docs-content-type: ASSEMBLY
    if not any(assembly_type_pattern.search(line) for line in lines):
        return False

    changed = False
    changed |= ensure_top_conditional(lines)
    changed |= ensure_bottom_conditionals(lines)
    changed |= ensure_context_variable(lines)
    changed |= ensure_include_spacing(lines)
    changed |= flag_illegal_headings(lines)
    changed |= flag_block_titles(lines)

    if changed and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return changed

# ------------------------
# Entry point: process all .adoc files in the given directory
# ------------------------
def main():
    parser = argparse.ArgumentParser(description="Fix and flag structural issues in assembly files.")
    parser.add_argument("directory", help="Directory containing assembly .adoc files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change but don’t modify files")
    args = parser.parse_args()

    fixed = 0
    for root, _, files in os.walk(args.directory):
        for file in files:
            if file.endswith(".adoc"):
                path = os.path.join(root, file)
                if fix_assembly_file(path, dry_run=args.dry_run):
                    print(f"✔ Fixed: {file}")
                    fixed += 1

    print(f"✅ Done. Files fixed: {fixed}")

if __name__ == "__main__":
    main()
