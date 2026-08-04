import ast

sample_code = """
def greet(name):
    return f"Hello, {name}!"

class Dog:
    def bark(self):
        return "Woof!"
"""

tree = ast.parse(sample_code)

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        # Extract the actual source code text for this function/class
        code_chunk = ast.get_source_segment(sample_code, node)
        
        print("=" * 50)
        print("Name:", node.name)
        print("Code:")
        print(code_chunk)