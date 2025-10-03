from pathlib import Path
import sys
import pytest

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from parser.parser import CustomParser, EXCLUDED_DIRS, EXCLUDED_EXTENSIONS

EXAMPLE_PATH = "../php_js_project_example/pomopensource"
LANG_SUFFIXES = {'.php', '.js', '.jsx', '.ts', '.tsx'}
project_test = (Path(__file__).resolve().parent / EXAMPLE_PATH).resolve()


def test_parse_file():
	if not project_test.exists():
		print(f"Test project path does not exist: {project_test}")
		return
	parser = CustomParser(str(project_test))
	ast = parser.set_ast()  # no argument needed
	print("AST object type:", type(ast))
	assert isinstance(ast, dict)

def test_extract_symbols():
	"""Test extraction of classes, properties, and methods from PHP files."""
	if not project_test.exists():
		print(f"Test project path does not exist: {project_test}")
		return
	parser = CustomParser(str(project_test))
	parser.set_ast()
	for file_name in parser._parsed_folder_tree.keys():
		if not file_name.endswith(".php"):
			continue
		symbols = parser.extract_symbols(file_name)  # no tree/code needed
		assert "file" in symbols and symbols["file"] == file_name
		assert "classes" in symbols
		for cls in symbols["classes"]:
			assert "class" in cls
			assert "properties" in cls
			assert "methods" in cls
		print(f"Symbols for {file_name}: {symbols}\n")


# Reusable helpers for folder/file exclusions
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
	if EXCLUDED_EXTENSIONS and file.name.endswith(tuple(EXCLUDED_EXTENSIONS)):
		return True
	suf = [s.lower() for s in file.suffixes]
	if len(suf) >= 2 and suf[-2:] == ['.blade', '.php']:
		return True
	return False


@pytest.mark.parametrize("project_rel", ["../php_js_project_example/pomopensource"])
def test_parse_folder_includes_all_non_ignored_files(project_rel):
	project_root = project_test
	assert project_root.exists(), f"Project path not found: {project_root}"

	parser = CustomParser(str(project_root))
	ast = parser.set_ast()
	actual = set(ast.keys())

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
		f"Missing (should have been parsed): {missing[:50]}{' …' if len(missing) > 50 else ''}\n"
		f"Unexpected (should NOT have been parsed): {unexpected[:50]}{' …' if len(unexpected) > 50 else ''}"
	)
