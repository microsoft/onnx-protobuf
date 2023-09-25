import os
import shutil

root_dir = "/home/vsts/.ivy2/local/com.microsoft.azure/onnx-protobuf_2.12"


def flatten_dir(top_dir):
    # Collect directories to delete
    directories_to_delete = []

    # Walk through all subdirectories
    for foldername, subfolders, filenames in os.walk(top_dir, topdown=False):

        # If we are not in the top-level directory, move files to the top-level directory
        if foldername != top_dir:
            for filename in filenames:
                source = os.path.join(foldername, filename)
                destination = os.path.join(top_dir, filename)

                # Check if a file with the same name already exists in the top-level directory
                if os.path.exists(destination):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    new_destination = os.path.join(top_dir, f"{base}_{counter}{ext}")

                    # Find a new destination path that does not exist yet
                    while os.path.exists(new_destination):
                        counter += 1
                        new_destination = os.path.join(top_dir, f"{base}_{counter}{ext}")

                    destination = new_destination

                # Move file
                shutil.move(source, destination)
                print(f"Moved: {source} to {destination}")

            # Add the foldername to the list of directories to delete
            directories_to_delete.append(foldername)

    # Delete the old subdirectories
    for directory in directories_to_delete:
        os.rmdir(directory)
        print(f"Deleted: {directory}")


for top_dir in os.listdir(root_dir):
    path_to_jars = os.path.join(root_dir, top_dir)
    flatten_dir(path_to_jars)

    for file in os.listdir(path_to_jars):
        if "_2.12" in file and top_dir not in file:
            old_file_path = os.path.join(path_to_jars, file)
            name_parts = file.split("_2.12")
            if name_parts[1].startswith(".") or name_parts[1].startswith("-"):
                sep_char = ""
            else:
                sep_char = "-"
            new_file = f"{name_parts[0]}_2.12-{top_dir}{sep_char}{name_parts[1]}"
            new_file_path = os.path.join(path_to_jars, new_file)
            shutil.move(old_file_path, new_file_path)
