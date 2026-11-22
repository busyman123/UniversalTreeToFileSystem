#!/usr/bin/env python3
import sys
import re
from pathlib import Path

def parse_and_build(tree_file_path: str):
    input_path = Path(tree_file_path)
    if not input_path.is_file():
        print(f"Error: File '{tree_file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    lines = input_path.read_text(encoding="utf-8").splitlines()
    
    # Stack stores tuples of (indentation_depth, Path_object)
    path_stack: list[tuple[int, Path]] = []

    for line_num, raw_line in enumerate(lines, start=1):
        # 1. Strip inline comments (e.g., "  # description")
        clean_line = re.sub(r'\s+#.*$', '', raw_line).rstrip()
        if not clean_line.strip():
            continue

        # 2. Detect if item is explicitly a directory (ends with '/')
        is_dir = clean_line.endswith('/')

        # 3. Measure prefix depth (spaces, tabs, and tree characters before the name)
        match = re.match(r'^([│├└─\s\t]*)', clean_line)
        prefix = match.group(1) if match else ""
        depth = len(prefix.replace('\t', '    '))

        # 4. Extract the actual file or folder name
        name = clean_line[len(prefix):].strip('/')
        if not name:
            continue

        # 5. Pop stack until we find the parent directory at a shallower depth
        while path_stack and path_stack[-1][0] >= depth:
            path_stack.pop()

        parent_path = path_stack[-1][1] if path_stack else Path.cwd()
        current_path = parent_path / name

        # 6. Create directory or file
        if is_dir:
            current_path.mkdir(parents=True, exist_ok=True)
            print(f"[DIR]  {current_path.relative_to(Path.cwd())}/")
        else:
            current_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.touch(exist_ok=True)
            print(f"[FILE] {current_path.relative_to(Path.cwd())}")

        # Push onto stack so nested children can resolve against it
        path_stack.append((depth, current_path))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <tree_structure.txt>", file=sys.stderr)
        sys.exit(1)

    parse_and_build(sys.argv[1])
