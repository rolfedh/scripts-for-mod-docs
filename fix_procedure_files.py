import os
import re
import argparse

# Allowed trailing block titles after .Procedure
ALLOWED_BLOCK_TITLES = {
    ".Verification", ".Troubleshooting", ".Troubleshooting steps",
    ".Next steps", ".Next step", ".Additional resources"
}

# Regex patterns
procedure_title_pattern = re.compile(r"^\.Procedure(\s.*)?$")
unordered_list_pattern = re.compile(r"^\s*[*+-]\s+")
ordered_list_pattern = re.compile(r"^\s*\d+\.\s+")
block_title_pattern = re.compile(r"^\.(\w+.*)")
procedure_type_pattern = re.compile(r':_mod-docs-content-type:\s*PROCEDURE')

def is_list_item(line):
    return bool(unordered_list_pattern.match(line) or ordered_list_pattern.match(line))

def fix_procedure_file(filepath, dry_run=False):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Only operate on files with :_mod-docs-content-type: PROCEDURE
    if not any(procedure_type_pattern.search(line) for line in lines):
        return False

    changed = False
    procedure_found = False
    procedure_line = None
    list_started = False
    last_list_line = None
    trailing_section_started = False
    in_code_block = False

    for idx, line in enumerate(lines):
        stripped = line.strip()

        # Track code block state BEFORE any flagging logic
        if stripped.startswith("----") or stripped.startswith("...."):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue  # Skip all flagging logic inside code blocks

        # Skip comments early
        if stripped.startswith("//"):
            continue

        # Detect .Procedure and check for embellishment
        match = procedure_title_pattern.match(stripped)
        if match:
            if not procedure_found:
                procedure_found = True
                procedure_line = idx
                if match.group(1):  # ".Procedure for..." = embellishment
                    lines.insert(idx, "// TODO: The .Procedure block title must not contain additional words.\n")
                    changed = True
            else:
                lines.insert(idx, "// TODO: Must include only one `.Procedure` block title and list.\n")
                changed = True
            continue

        # Validate list follows .Procedure
        if procedure_found and idx > procedure_line and not list_started:
            if is_list_item(stripped):
                list_started = True
                last_list_line = idx

                # Find the last line of the list (including continuations)
                temp_idx = idx + 1
                while temp_idx < len(lines):
                    next_line = lines[temp_idx].strip()
                    if next_line == '+' or next_line.startswith('.') or next_line.startswith('['):
                        temp_idx += 1
                        continue
                    if next_line.startswith('----') or next_line.startswith('....'):
                        temp_idx += 1
                        continue
                    if next_line == '':  # Stop at blank line
                        temp_idx += 1
                        break
                    break
                last_list_line = temp_idx - 1

        # Only flag if the first non-blank, non-comment line after .Procedure is not a list item or block title
        if (
            procedure_found
            and idx > procedure_line
            and not list_started
        ):
            if not stripped or stripped.startswith("//"):
                continue  # Skip blank lines and comments
            if not (
                is_list_item(stripped)
                or stripped.startswith(". ")
                or stripped.startswith(".. ")
            ):
                lines.insert(
                    procedure_line + 1,
                    "// TODO: Must include a `.Procedure` block title followed by an ordered or unordered list.\n"
                )
                changed = True
            list_started = True

        if list_started and is_list_item(stripped):
            last_list_line = idx

        # After the list, only allow certain block titles or allowed content
        if procedure_found and last_list_line is not None and idx > last_list_line:
            prev_line = lines[idx - 1].strip() if idx > 0 else ''
            # Allow continuation block after '+'
            if prev_line == '+':
                continue
            # Allow continuation paragraph
            if prev_line != '' and not block_title_pattern.match(stripped):
                continue
            # Check for allowed block titles
            if block_title_pattern.match(stripped):
                title = stripped.split()[0]
                prev_line_full = lines[idx - 1].strip() if idx > 0 else ''
                should_flag = True
                if title == '.Additional' and prev_line_full == '[role="_additional-resources"]':
                    should_flag = False
                if should_flag and title not in ALLOWED_BLOCK_TITLES:
                    lines.insert(idx, "// TODO: Only `.Procedure`, `.Verification`, `.Troubleshooting`, `.Next steps`, etc. are allowed block titles in procedure modules.\n")
                    changed = True
                # Special case: .Additional resources preceded by [role="_additional-resources"]
                if stripped == '.Additional resources' and prev_line_full == '[role=\"_additional-resources\"]':
                    continue  # Valid additional resources section
                break  # Stop after first invalid section

            elif (
                stripped
                and not stripped.startswith("//")
                and not (
                    stripped.startswith("* ")
                    or stripped.startswith("** ")
                    or stripped.startswith(". ")
                    or stripped.startswith(".. ")
                    or stripped.startswith('[role="_additional-resources"]')
                )
            ):
                lines.insert(idx, "// TODO: Content found after last procedure step. Only allowed sections may follow.\n")
                changed = True
                break  # Stop after first invalid section
    if not procedure_found:
        lines.insert(0, "// TODO: Must include a `.Procedure` block title followed by an ordered or unordered list.\n")
        changed = True

    if changed and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return changed

def main():
    parser = argparse.ArgumentParser(description="Fix or flag issues in PROCEDURE modules.")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change, but don’t write files")
    args = parser.parse_args()

    changed_files = 0
    for root, _, files in os.walk(args.directory):
        for file in files:
            if file.endswith(".adoc"):
                filepath = os.path.join(root, file)
                # Only process files with :_mod-docs-content-type: PROCEDURE
                with open(filepath, "r", encoding="utf-8") as f:
                    if ":_mod-docs-content-type: PROCEDURE" not in f.read():
                        continue
                print(f"Checking: {file}")
                if fix_procedure_file(filepath, dry_run=args.dry_run):
                    changed_files += 1

    print(f"✅ Done. Files fixed: {changed_files}.")

if __name__ == "__main__":
    main()
