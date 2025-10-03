from pathlib import Path

import tree_sitter_php as tsphp
import tree_sitter_javascript as tsjs
from tree_sitter import Language, Parser, Node

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


class CustomParser:

	def __init__(self, project_path: str):
		self.folder_path = Path(project_path).resolve()
		self._parsed_folder_tree = {}  # {relative_path: tree}
		self._file_codes = {}

	def _parse_file(self, file_path, language):
		parser = Parser()
		parser.language = language
		code = Path(file_path).read_text()
		tree = parser.parse(bytes(code, "utf8"))
		return tree, code  # return code too for symbol extraction

	def set_ast(self):
		"""Parse all files in folder and store ASTs internally"""
		res = {}
		self._file_codes = {}
		for file in self.folder_path.rglob('*'):
			if not file.is_file():
				continue
			rel = file.relative_to(self.folder_path)
			rel_posix = rel.as_posix()
			if any(f'/{Path(d).as_posix().strip("/")}/' in f'/{rel_posix}/' for d in EXCLUDED_DIRS):
				continue
			if file.name.endswith(EXCLUDED_EXTENSIONS) or file.suffixes[-2:] == ['.blade', '.php']:
				continue
			if file.suffix == ".php":
				lang = PHP_LANGUAGE
			elif file.suffix in (".js", ".jsx", ".ts", ".tsx"):
				lang = JS_LANGUAGE
			else:
				continue

			tree, code = self._parse_file(file, lang)
			res[rel_posix] = tree
			self._file_codes[rel_posix] = code

		self._parsed_folder_tree = res
		return res

	def extract_symbols(self, file_path: str):
		"""Use internal AST and code to extract symbols; no parameters for tree/code needed"""
		tree = self._parsed_folder_tree[file_path]
		code = self._file_codes[file_path]
		root = tree.root_node
		result = {"file": file_path, "classes": []}

		def text(node):
			return code[node.start_byte:node.end_byte]

		def walk_class(node):
			info = {"class": None, "extends": None, "properties": [], "methods": []}
			for child in node.children:
				if child.type == "name" and info["class"] is None:
					info["class"] = text(child)
				elif child.type == "base_clause":
					for c in child.children:
						if c.type in ("name", "qualified_name"):
							info["extends"] = text(c)
				elif child.type == "declaration_list":
					for member in child.children:
						if member.type == "property_declaration":
							for v in member.children:
								if v.type == "property_element":
									for vv in v.children:
										if vv.type == "variable_name":
											info["properties"].append(text(vv))
						elif member.type == "method_declaration":
							m = {"name": None, "return": None}
							for c in member.children:
								if c.type == "name" and m["name"] is None:
									m["name"] = text(c)
								elif c.type in ("named_type", "primitive_type", "qualified_name"):
									m["return"] = text(c)
							info["methods"].append(m)
			return info

		for child in root.children:
			if child.type == "class_declaration":
				result["classes"].append(walk_class(child))

		return result
