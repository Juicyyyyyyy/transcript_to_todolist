from pathlib import Path

import tree_sitter_php as tsphp
import tree_sitter_javascript as tsjs
from tree_sitter import Language, Parser

PHP_LANGUAGE = Language(tsphp.language_php())
JS_LANGUAGE = Language(tsjs.language())
EXCLUDED_DIRS = [
	'vendor',
	'node_modules',
	'.git',
	'storage',
	'bootstrap/cache',
	'public/build',
	'dist',
	'.idea',
	'.vscode',
	'.cache',
	'coverage',
	'bootstrap'
]

EXCLUDED_EXTENSIONS = ('.blade.php',)

class Parser_:

	@staticmethod
	def parse_file(file_path, language):
		parser = Parser()
		parser.language = language
		code = Path(file_path).read_text()
		tree = parser.parse(bytes(code, "utf8"))
		return tree

	@staticmethod
	def parse_folder(folder_path):
		root = Path(folder_path).resolve()
		res = {}
		for file in root.rglob('*'):
			if not file.is_file():
				continue

			rel = file.relative_to(root)
			rel_posix = rel.as_posix()

			# ---- directory exclusions (supports nested like "public/build") ----
			rel_slashes = f'/{rel_posix}/'
			if any(f'/{Path(d).as_posix().strip("/")}/' in rel_slashes for d in EXCLUDED_DIRS):
				continue

			# ---- file pattern exclusions (e.g., *.blade.php) ----
			# endswith accepts a tuple -> one check, skips the file entirely
			if file.name.endswith(EXCLUDED_EXTENSIONS) or file.suffixes[-2:] == ['.blade', '.php']:
				continue

			# ---- language selection ----
			if file.suffix == '.php':
				lang = PHP_LANGUAGE
			elif file.suffix in ('.js', '.jsx', '.ts', '.tsx'):
				lang = JS_LANGUAGE
			else:
				continue

			res[rel_posix] = Parser_.parse_file(file, lang)
		return res

	@staticmethod
	def toString(tree, code=None, named_only=True):
		"""
		Pretty-print a Tree-sitter AST as an S-expression,
		including the actual source text for leaves like identifiers/strings.
		"""
		if tree is None:
			return ""

		if code is None:
			raise ValueError("Need original source code to include variable/function names")

		root = tree.root_node

		def sexp(node):
			# Select children
			children = [c for c in node.children if (not named_only) or c.is_named]

			# Leaf node
			if not children:
				text = code[node.start_byte:node.end_byte].strip()
				if text:
					return f"({node.type}:'{text}')"
				else:
					return node.type

			# Internal node
			return f"({node.type} {' '.join(sexp(c) for c in children)})"

		return sexp(root)


