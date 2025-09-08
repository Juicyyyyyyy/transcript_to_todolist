from pathlib import Path

from parser.parser import Parser_

import pytest

from parser.parser import Parser_, EXCLUDED_DIRS, EXCLUDED_EXTENSIONS

EXAMPLE_PATH = "../php_js_project_example/pomopensource"
LANG_SUFFIXES = {'.php', '.js', '.jsx', '.ts', '.tsx'}
project_test = (Path(__file__).resolve().parent / EXAMPLE_PATH).resolve()


def test_parse_file():
	# project_test = "../php_js_test_project/pomopensource"
	if not project_test.exists():
		print(f"Test project path does not exist: {project_test}")
		return
	ast = Parser_.parse_folder(project_test)
	print("ast object: " + str(ast))
#test_parse_file()

def test_toString():
	if not project_test.exists():
		print(f"Test project path does not exist: {project_test}")
		return
	ast = Parser_.parse_folder(project_test)
	for file_name, tree in ast.items():
		file_path = project_test / file_name
		code = Path(file_path).read_text()
		sexp = Parser_.toString(tree, code)
		print(f"S-expression for {file_name}:\n{sexp}\n")

test_toString()

def _in_excluded_dir(rel: Path, excluded_dirs) -> bool:
    """Segment-aware check: supports nested entries like 'public/build' or 'bootstrap/cache'."""
    rel_posix = rel.as_posix()
    rel_slashes = f'/{rel_posix}/'
    for d in excluded_dirs:
        seg = Path(d).as_posix().strip('/')
        if f'/{seg}/' in rel_slashes:
            return True
    return False

def _is_excluded_file(file: Path) -> bool:
    # Respect explicit patterns like ".blade.php"
    if EXCLUDED_EXTENSIONS and file.name.endswith(tuple(EXCLUDED_EXTENSIONS)):
        return True
    # Extra safety: detect ".blade.php" via suffixes too
    suf = [s.lower() for s in file.suffixes]
    if len(suf) >= 2 and suf[-2:] == ['.blade', '.php']:
        return True
    return False

@pytest.mark.parametrize("project_rel", ["../php_js_project_example/pomopensource"])
def test_parse_folder_includes_all_non_ignored_files(project_rel):
    project_root = project_test
    assert project_root.exists(), f"Project path not found: {project_root}"

    # Actual parsed files
    ast = Parser_.parse_folder(project_root)
    actual = set(ast.keys())  # relative posix paths (as produced by Parser_.parse_folder)

    # Expected files by walking the FS with the SAME intent as the parser
    expected = set()
    for file in project_root.rglob('*'):
        if not file.is_file():
            continue
        rel = file.relative_to(project_root)

        if _in_excluded_dir(rel, EXCLUDED_DIRS):
            continue
        if _is_excluded_file(file):
            continue
        if file.suffix.lower() not in LANG_SUFFIXES:
            continue

        expected.add(rel.as_posix())

    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)

    assert not missing and not unexpected, (
        "Parsed set does not match expected.\n"
        f"Missing (should have been parsed): {missing[:50]}{' …' if len(missing)>50 else ''}\n"
        f"Unexpected (should NOT have been parsed): {unexpected[:50]}{' …' if len(unexpected)>50 else ''}"
    )