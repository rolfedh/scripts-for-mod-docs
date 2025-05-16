import os
import re
import argparse

# ------------------------
# Regular expression patterns for detecting AsciiDoc content structure
# ------------------------
mod_docs_type_pattern = re.compile(r'^:.*_mod-docs-content-type:', re.MULTILINE)
topic_id_pattern = re.compile(r'^\[id="[^"]+_\{context\}"\]', re.MULTILINE)
h1_title_pattern = re.compile(r'^(= .+)', re.MULTILINE)
image_pattern = re.compile(r'(image::[^\[]+\[)([^\]]*)(\])')

# Determine content type based on file name prefix (supports _ and -)
def get_doc_type(filename):
    prefix_map = {
        "proc": "PROCEDURE",
        "con": "CONCEPT",
        "ref": "REFERENCE",
        "assembly": "ASSEMBLY"
    }
    for prefix, doc_type in prefix_map.items():
        if filename.startswith(f"{prefix}_") or filename.startswith(f"{prefix}-"):
            return doc_type
    return None

# Ensure a blank line follows the level 0 (=) title
def ensure_blank_line_after_title(lines):
    for i in range(len(lines) - 1):
        if lines[i].startswith('= ') and lines[i + 1].strip() != "":
            lines.insert(i + 1, "\n")
            return lines, True
    return lines, False

# Check whether a short introductory paragraph exists after the H1 title
def has_short_intro(lines):
    h1_index = next((i for i, line in enumerate(lines) if line.startswith("= ")), None)
    if h1_index is None or h1_index + 1 >= len(lines):
        return False
    for line in lines[h1_index + 1:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("//") or stripped.startswith(":"):
            continue
        if stripped.startswith((".", "*", "-", "+", "=", "[", "include::", "image::", "----", "....")):
            return False
        if len(stripped) > 10 and any(c.islower() for c in stripped) and (stripped.endswith('.') or len(stripped.split()) > 5):
            return True
        return False
    return False

# Fix or flag images that lack alt text or use unquoted alt text
def fix_images(lines):
    new_lines = []
    for line in lines:
        if line.strip().startswith("image::"):
            match = image_pattern.match(line.strip())
            if match:
                prefix, alt_text, suffix = match.groups()
                if not alt_text.strip():
                    new_lines.append(line.rstrip() + "\n")
                    new_lines.append("// TODO: Add descriptive alt text in quotation marks for accessibility.\n")
                elif not (alt_text.startswith('"') and alt_text.endswith('"')):
                    quoted = f'{prefix}"{alt_text.strip()}"{suffix}\n'
                    new_lines.append(quoted)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    return new_lines

# Apply all fixes to a single AsciiDoc file
def fix_file(filepath, dry_run=False):
    filename = os.path.basename(filepath)
    doc_type = get_doc_type(filename)
    if not doc_type:
        return False, f"Unknown file type for: {filename}"

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False

    if not any(mod_docs_type_pattern.match(line) for line in lines):
        lines.insert(0, f":_mod-docs-content-type: {doc_type}\n")
        changed = True

    if not any(topic_id_pattern.match(line) for line in lines):
        topic_id = os.path.splitext(filename)[0]
        lines.insert(0, f'[id="{topic_id}_{{context}}"]\n')
        changed = True

    h1_indexes = [i for i, line in enumerate(lines) if h1_title_pattern.match(line)]
    if len(h1_indexes) > 1:
        lines.insert(h1_indexes[1], '// TODO: Review this file to ensure it has only one level zero "= " title .\n')
        changed = True

    lines, inserted_blank = ensure_blank_line_after_title(lines)
    if inserted_blank:
        changed = True

    if not has_short_intro(lines):
        h1_index = next((i for i, line in enumerate(lines) if line.startswith("= ")), None)
        if h1_index is not None:
            lines.insert(h1_index + 2, '// TODO: Add a short introductory sentence here that explains the purpose of this module or assembly.\n')
            lines.insert(h1_index + 3, '\n')
            changed = True

    updated_lines = fix_images(lines)
    if updated_lines != lines:
        lines = updated_lines
        changed = True

    if changed and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return changed, None

# Entry point: parse args and apply fixes to all .adoc files in the directory
def main():
    parser = argparse.ArgumentParser(description="Auto-fix AsciiDoc issues including metadata, images, structure, and intro detection.")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change, but don’t write files")
    args = parser.parse_args()

    changed_files = 0
    skipped_files = 0
    for root, _, files in os.walk(args.directory):
        for file in files:
            if file.endswith(".adoc"):
                path = os.path.join(root, file)
                changed, error = fix_file(path, dry_run=args.dry_run)
                if error:
                    skipped_files += 1
                    print(f"Skipped {file}: {error}")
                elif changed:
                    changed_files += 1
                    print(f"Fixed {file}")

    print(f"✅ Done. Files fixed: {changed_files}. Files skipped: {skipped_files}.")

if __name__ == "__main__":
    main()
