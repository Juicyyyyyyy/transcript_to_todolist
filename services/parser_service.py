from pathlib import Path
from typing import Dict, Any

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


class ParserService:
	"""Service for parsing project files and extracting symbols"""

	def __init__(self):
		self._parsed_folder_tree = {}  # {relative_path: tree}
		self._file_codes = {}
		self.folder_path = None

	def _parse_file(self, file_path, language):
		parser = Parser()
		parser.language = language
		code = Path(file_path).read_text()
		tree = parser.parse(bytes(code, "utf8"))
		return tree, code

	def set_ast(self, project_path: str) -> Dict[str, Any]:
		"""Parse all files in folder and store ASTs internally"""
		self.folder_path = Path(project_path).resolve()
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

	def extract_symbols(self, file_path: str) -> Dict[str, Any]:
		"""Extract symbols from a parsed file using internal AST and code"""
		if file_path not in self._parsed_folder_tree:
			raise ValueError(f"File {file_path} not found in parsed tree. Run set_ast first.")
		
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

	def extract_all_symbols(self) -> str:
		"""Extract symbols from all parsed files and return as a formatted string"""
		if not self._parsed_folder_tree:
			raise ValueError("No files parsed. Run set_ast first.")
		
		all_symbols = []
		
		for file_path in sorted(self._parsed_folder_tree.keys()):
			try:
				symbols = self.extract_symbols(file_path)
				all_symbols.append(symbols)
			except Exception as e:
				# Skip files that can't be parsed
				continue
		
		return self._format_symbols_for_openai(all_symbols)
	
	def _format_symbols_for_openai(self, all_symbols: list) -> str:
		"""Format extracted symbols into a readable string for OpenAI"""
		output_lines = []
		output_lines.append("# Project Structure Analysis\n")
		output_lines.append(f"Total files analyzed: {len(all_symbols)}\n")
		output_lines.append("=" * 80 + "\n\n")
		
		for file_data in all_symbols:
			file_path = file_data.get("file", "Unknown")
			classes = file_data.get("classes", [])
			
			output_lines.append(f"## File: {file_path}\n")
			
			if not classes:
				output_lines.append("  No classes found in this file.\n\n")
				continue
			
			for cls in classes:
				class_name = cls.get("class_name") or cls.get("class", "Unknown")
				extends = cls.get("extends")
				properties = cls.get("properties", [])
				methods = cls.get("methods", [])
				
				output_lines.append(f"\n### Class: {class_name}")
				if extends:
					output_lines.append(f" extends {extends}")
				output_lines.append("\n")
				
				if properties:
					output_lines.append("  **Properties:**\n")
					for prop in properties:
						output_lines.append(f"    - {prop}\n")
				
				if methods:
					output_lines.append("  **Methods:**\n")
					for method in methods:
						method_name = method.get("name", "Unknown")
						return_type = method.get("return_type") or method.get("return", "void")
						output_lines.append(f"    - {method_name}(): {return_type}\n")
				
				output_lines.append("\n")
			
			output_lines.append("-" * 80 + "\n\n")
		
		return "".join(output_lines)


