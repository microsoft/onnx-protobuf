import os
import shutil

root_dir = "~/.ivy2/local/com.microsoft.azure/onnx-protobuf_2.12"
for top_dir in os.listdir(root_dir):



    # Walk through the directory
    for root, dirs, files in os.walk(os.path.join(root_dir, top_dir)):
        for file in files:
            # Construct the full file path
            full_file_path = os.path.join(root, file)

            # Extract the version number from the file name
            base_name, ext = os.path.splitext(file)
            name_parts = base_name.split("_")
            new_version_number = name_parts[1] + "-" + top_dir
            new_base_name = name_parts[0] + "_" + new_version_number

            # Construct the new file name
            new_file_name = new_base_name + ext

            # Construct the new file path
            new_file_path = os.path.join(top_dir, new_file_name)

            # Move the file to the top-level directory with the new name
            shutil.move(full_file_path, new_file_path)

    # Optionally, remove the subdirectories if they are now empty
    for root, dirs, _ in os.walk(top_dir, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
