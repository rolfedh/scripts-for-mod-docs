import os
import re
import argparse

# ------------------------
# Regex patterns
# ------------------------
context_pattern = re.compile(r':_mod-docs-content-type:\s*(CONCEPT|REFERENCE)')
heading_pattern = re.compile(r'^(===+)\s+\S')  # Matches headings at level 2 or deeper
block_title_pattern = re.compile(r'^\.[A-Za-z].+')
instructional_list_pattern = re.compile(r'^(\d+\.|\*|\-|\.)\s+\S')

# Conservative list of directive verbs
imperative_verbs = [
    "configure", "add", "set", "click", "open", "run", "create", "delete", "update", "install", "enable", "disable"
]

# ------------------------
# Check for imperatives and instructional tone in lists or paragraphs
# ------------------------
def contains_instructional_content(lines):
    link_only_pattern = re.compile(r'^(?:\*|\d+\.)\s+link:[^\[]+\[[^\]]+\]\s*$')

    in_list_item = False
    for i, line in enumerate(lines):
        stripped = line.strip().lower()

        # Skip comments and blank lines
        if not stripped or stripped.startswith("//"):
            continue

        # Skip known safe forms
        if (
            stripped.startswith("link:") or
            "see link:" in stripped or
            (stripped.startswith("for more information") and "see" in stripped) or
            link_only_pattern.match(stripped)
        ):
            continue

        # If it's a new list item, track it
        if instructional_list_pattern.match(stripped):
            in_list_item = True

            # Check if it's just a link
            if link_only_pattern.match(stripped):
                continue

            # Split on punctuation to isolate the first meaningful line
            parts = stripped.split(":", 1)
            if len(parts) > 1:
                next_line = parts[1].strip()
            else:
                next_line = stripped

            # Check first word is imperative form
            for verb in imperative_verbs:
                if next_line.startswith(verb + " "):
                    first_word = next_line.split()[0]
                    if first_word == verb:
                        return i
            continue

        # Handle follow-up lines (do not flag them)
        if in_list_item:
            continue

        # Catch imperatives outside lists
        for verb in imperative_verbs:
            if stripped.startswith(verb + " ") and stripped.split()[0] == verb:
                return i

    return None




# ------------------------
# Validate block titles except for allowed ones
# ------------------------
def flag_block_titles(lines):
    changed = False
    insertions = []
    skip_next_line_types = ("----", "....", "|====", "|===", "====")
    formatting_pattern = re.compile(r'^\[.*\]$')

    for idx, line in enumerate(lines):
        line_stripped = line.strip()

        if block_title_pattern.match(line_stripped):
            if line_stripped in [".Additional resources", ".Next steps"]:
                continue

            is_valid_structure = False
            lookahead_lines = lines[idx+1:idx+6]

            for la_line in lookahead_lines:
                la_stripped = la_line.strip()
                if not la_stripped:
                    continue
                if formatting_pattern.match(la_stripped):
                    continue
                if any(la_stripped.startswith(marker) for marker in skip_next_line_types):
                    is_valid_structure = True
                    break
                break  # not a formatting or structural marker

            if not is_valid_structure:
                insertions.append(idx)

    for idx in reversed(insertions):
        lines.insert(idx, "// TODO: Unexpected block title. Use only `.Next steps` or `.Additional resources` in concept/reference modules.\n")
        changed = True

    return changed


# ------------------------
# Main fix function for a single file
# ------------------------
def fix_conref_file(filepath, dry_run=False):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    content_type = None
    for line in lines:
        match = context_pattern.search(line)
        if match:
            content_type = match.group(1)
            break

    if content_type not in ["CONCEPT", "REFERENCE"]:
        return False

    changed = False

    # Flag instructions
    instruct_index = contains_instructional_content(lines)
    if instruct_index is not None:
        lines.insert(instruct_index, "// TODO: Avoid instructions in concept and reference modules.\n")
        changed = True

    # Flag .Procedure and .Prerequisites blocks (iterate in reverse)
    for idx in reversed(range(len(lines))):
        if lines[idx].strip() in [".Procedure", ".Prerequisites"]:
            lines.insert(
                idx,
                "// TODO: Consider changing the :_mod-docs-content-type: to PROCEDURE or moving this procedure to a new file.\n"
            )
            changed = True
            break

    # Flag numbered . steps that start with a capital imperative verb
    numbered_step_pattern = re.compile(r'^\.\s+([A-Z][a-z]+)')
    for idx, line in enumerate(lines):
        match = numbered_step_pattern.match(line.strip())
        if match and match.group(1).lower() in imperative_verbs:
            lines.insert(idx, "// TODO: Consider changing the :_mod-docs-content-type: to PROCEDURE or moving this procedure to a new file.\n")
            changed = True
            break


    # Flag level 2+ headings (excluding admonition delimiters like ====)
    for idx, line in enumerate(lines):
        if heading_pattern.match(line.strip()) and line.strip() != "====":
            lines.insert(idx, "// TODO: This file should not contain a level 2 (===) section title (H3) or lower.\n")
            changed = True
            break

    # Flag invalid block titles
    changed |= flag_block_titles(lines)

    if changed and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return changed

# ------------------------
# CLI wrapper
# ------------------------
def main():
    parser = argparse.ArgumentParser(description="Fix and flag issues in CONCEPT and REFERENCE modules.")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    args = parser.parse_args()

    fixed = 0
    for root, _, files in os.walk(args.directory):
        for file in files:
            if file.endswith(".adoc"):
                path = os.path.join(root, file)
                print(f"Checking: {file}")
                if fix_conref_file(path, dry_run=args.dry_run):
                    print(f"✔ Fixed: {file}")
                    fixed += 1

    print(f"✅ Done. Files fixed: {fixed}")

if __name__ == "__main__":
    main()
