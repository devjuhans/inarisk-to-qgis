import os
import zipfile

def create_plugin_zip():
    # The name of the folder inside the zip (PEP 8 compliant)
    plugin_dir_name = "inarisk_to_qgis"
    
    # The name of the output zip file
    zip_filename = "inarisk_to_qgis.zip"
    
    # Files and extensions to exclude from the zip
    exclude_files = ["build_zip.py", zip_filename, ".gitignore", ".gitattributes"]
    exclude_dirs = [".git", "__pycache__"]
    
    # Create the zip file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        print(f"Creating {zip_filename}...")
        for root, dirs, files in os.walk("."):
            # Exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file not in exclude_files and not file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    # The path inside the zip file
                    arcname = os.path.join(plugin_dir_name, os.path.relpath(file_path, "."))
                    print(f"Adding {file_path} as {arcname}")
                    zipf.write(file_path, arcname)
                    
    print(f"\nSuccess! You can now upload '{zip_filename}' to the QGIS plugin repository.")

if __name__ == "__main__":
    create_plugin_zip()
