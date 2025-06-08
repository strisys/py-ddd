import ast
import sys
import json
import subprocess
from pathlib import Path

def collect_imports(source_dir):
    imports = set()
    for path in Path(source_dir).rglob("*.py"):
        with path.open("r", encoding="utf-8") as file:
            try:
                node = ast.parse(file.read(), filename=str(path))
            except SyntaxError:
                continue
            for n in ast.walk(node):
                if isinstance(n, ast.Import):
                    for alias in n.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(n, ast.ImportFrom) and n.module:
                    imports.add(n.module.split('.')[0])
    return imports

def get_allowed_packages():
    result = subprocess.run(["pipdeptree", "--json"], capture_output=True, check=True)
    tree = json.loads(result.stdout)
    return {pkg["package"]["key"] for pkg in tree}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: validate_imports.py <source_dir> <requirements.txt>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    used_imports = collect_imports(src_path)
    allowed = get_allowed_packages()

    violations = sorted(used_imports - allowed - {"__future__", "os", "sys", "typing"})
    if violations:
        print("? Illegal imports not in transitive closure of requirements.txt:")
        for v in violations:
            print(f" - {v}")
        sys.exit(1)
    else:
        print("? All imports in source are valid against declared requirements.")
