from pathlib import Path
from typing import Dict, Any

import tree_sitter_php as tsphp
import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser

PHP_LANGUAGE = Language(tsphp.language_php())
JS_LANGUAGE = Language(tsjs.language())
TS_LANGUAGE = Language(tsts.language_typescript())
TSX_LANGUAGE = Language(tsts.language_tsx())
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
			elif file.suffix == ".tsx":
				lang = TSX_LANGUAGE
			elif file.suffix == ".ts":
				lang = TS_LANGUAGE
			elif file.suffix in (".js", ".jsx"):
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

		# Determine file type
		is_js_ts = file_path.endswith(('.js', '.jsx', '.ts', '.tsx'))

		if is_js_ts:
			# JavaScript/TypeScript extraction
			self._extract_js_ts_symbols(root, result, text)
		else:
			# PHP extraction
			self._extract_php_symbols(root, result, text)

		return result

	def _extract_php_symbols(self, root, result, text):
		"""Extract symbols from PHP AST"""
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

	def _extract_js_ts_symbols(self, root, result, text):
		"""Extract symbols from JavaScript/TypeScript AST"""
		def walk_node(node):
			# Handle class declarations
			if node.type == "class_declaration":
				class_info = self._extract_js_class(node, text)
				if class_info:
					result["classes"].append(class_info)
			
			# Handle interface declarations
			elif node.type == "interface_declaration":
				interface_info = self._extract_js_interface(node, text)
				if interface_info:
					result["classes"].append(interface_info)
			
			# Handle export statements
			elif node.type == "export_statement":
				for child in node.children:
					if child.type in ("class_declaration", "interface_declaration", "function_declaration", "lexical_declaration"):
						walk_node(child)
			
			# Handle function declarations
			elif node.type == "function_declaration":
				func_info = self._extract_js_function(node, text)
				if func_info:
					result["classes"].append(func_info)
			
			# Handle lexical declarations (const/let with arrow functions)
			elif node.type == "lexical_declaration":
				func_info = self._extract_js_lexical_function(node, text)
				if func_info:
					result["classes"].append(func_info)

		# Walk through all top-level nodes
		for child in root.children:
			walk_node(child)

	def _extract_js_class(self, node, text):
		"""Extract information from a JavaScript/TypeScript class"""
		info = {"class": None, "extends": None, "properties": [], "methods": [], "type": "class"}
		
		for child in node.children:
			if child.type == "type_identifier" or child.type == "identifier":
				if info["class"] is None:
					info["class"] = text(child)
			elif child.type == "class_heritage":
				for c in child.children:
					if c.type == "identifier" or c.type == "type_identifier":
						info["extends"] = text(c)
			elif child.type == "class_body":
				for member in child.children:
					if member.type == "field_definition" or member.type == "public_field_definition":
						prop_info = self._extract_property_with_type(member, text)
						if prop_info:
							info["properties"].append(prop_info)
					elif member.type == "method_definition":
						method_info = self._extract_js_method(member, text)
						if method_info:
							info["methods"].append(method_info)
		
		return info if info["class"] else None

	def _extract_js_interface(self, node, text):
		"""Extract information from a TypeScript interface"""
		info = {"class": None, "extends": None, "properties": [], "methods": [], "type": "interface"}
		
		for child in node.children:
			if child.type == "type_identifier":
				if info["class"] is None:
					info["class"] = text(child)
			elif child.type == "extends_clause" or child.type == "extends_type_clause":
				for c in child.children:
					if c.type == "type_identifier":
						info["extends"] = text(c)
			elif child.type == "object_type" or child.type == "interface_body":
				for member in child.children:
					if member.type == "property_signature":
						prop_info = self._extract_property_with_type(member, text)
						if prop_info:
							info["properties"].append(prop_info)
					elif member.type == "method_signature":
						method_info = self._extract_js_method(member, text)
						if method_info:
							info["methods"].append(method_info)
		
		return info if info["class"] else None

	def _extract_js_function(self, node, text):
		"""Extract information from a function declaration"""
		info = {"class": None, "methods": [], "type": "function"}
		
		for child in node.children:
			if child.type == "identifier":
				if info["class"] is None:
					info["class"] = text(child)
					break
		
		return info if info["class"] else None

	def _extract_js_lexical_function(self, node, text):
		"""Extract information from const/let function declarations"""
		for child in node.children:
			if child.type == "variable_declarator":
				func_name = None
				for c in child.children:
					if c.type == "identifier":
						func_name = text(c)
					elif c.type in ("arrow_function", "function"):
						if func_name:
							return {"class": func_name, "methods": [], "type": "function"}
		return None

	def _extract_js_method(self, node, text):
		"""Extract method information from a class method or interface method"""
		method_info = {"name": None, "return": None}
		
		for child in node.children:
			if child.type == "property_identifier" or child.type == "identifier":
				if method_info["name"] is None:
					method_info["name"] = text(child)
			elif child.type == "type_annotation":
				for c in child.children:
					if c.type in ("type_identifier", "predefined_type"):
						method_info["return"] = text(c)
		
		return method_info if method_info["name"] else None

	def _get_property_name(self, node, text):
		"""Get property name from a field or property signature"""
		for child in node.children:
			if child.type in ("property_identifier", "identifier"):
				return text(child)
		return None

	def _extract_property_with_type(self, node, text):
		"""Extract property name and type annotation from a field or property signature"""
		prop_name = None
		type_annotation = None
		
		for child in node.children:
			if child.type in ("property_identifier", "identifier"):
				prop_name = text(child)
			elif child.type == "type_annotation":
				# Get the type from the type_annotation node
				for c in child.children:
					if c.type in ("type_identifier", "predefined_type", "union_type", "literal_type"):
						type_annotation = text(c)
						break
		
		if prop_name:
			return f"{prop_name}: {type_annotation}" if type_annotation else prop_name
		return None

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
		
		# Filter out files with no symbols
		files_with_symbols = [f for f in all_symbols if f.get("classes", [])]
		
		output_lines.append("# Project Structure Analysis\n")
		output_lines.append(f"Total files with symbols: {len(files_with_symbols)}\n")
		output_lines.append("=" * 80 + "\n\n")
		
		for file_data in files_with_symbols:
			file_path = file_data.get("file", "Unknown")
			classes = file_data.get("classes", [])
			
			output_lines.append(f"## File: {file_path}\n")
			
			for cls in classes:
				class_name = cls.get("class_name") or cls.get("class", "Unknown")
				extends = cls.get("extends")
				properties = cls.get("properties", [])
				methods = cls.get("methods", [])
				symbol_type = cls.get("type", "class")
				
				# Format header based on type
				if symbol_type == "interface":
					output_lines.append(f"\n### Interface: {class_name}")
				elif symbol_type == "function":
					output_lines.append(f"\n### Function: {class_name}")
				else:
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


