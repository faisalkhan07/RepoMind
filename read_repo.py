import os

for root, dirs, files in os.walk("micrograd"):
    for filename in files:
        if filename.endswith(".py"):
            filepath = os.path.join(root, filename)
            
            # Open and read the file's content
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            print("=" * 50)
            print("File:", filepath)
            print("Number of characters:", len(content))