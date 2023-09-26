import shutil
import os
import subprocess
import re
import getpass
import glob

current_username = getpass.getuser()

root_dir = f"/home/{current_username}/.ivy2/local/com.microsoft.azure/onnx-protobuf_2.12"


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



# Step 1: Look for gpg password file and secret key file in the /tmp dir
gpg_files = os.listdir('/tmp')
password_file = None
secret_key_file = None

for file in gpg_files:
    if re.match(r'keypw\d+\.txt$', file):
        password_file = os.path.join('/tmp', file)
    elif re.match(r'secret\d+\.asc$', file):
        secret_key_file = os.path.join('/tmp', file)

if password_file is None or secret_key_file is None:
    raise Exception('GPG password file or secret key file not found.')

# Step 2: Import the gpg key
import_command = ['gpg', '--batch', '--yes', '--passphrase-file', password_file, '--import', secret_key_file]
subprocess.run(import_command, check=True)

# Step 3: Get the current username and construct the jar file path
jar_file_pattern = f"/home/{current_username}/.ivy2/local/com.microsoft.azure/onnx-protobuf_2.12/*/onnx-protobuf_2.12-*.jar"
jar_files = [f for f in glob.glob(jar_file_pattern)]

if not jar_files:
    raise Exception('Jar file not found.')

# We will use the first found jar file for signing
jar_file_to_sign = jar_files[0]

# Step 4: Sign the jar
sign_command = ['gpg', '--batch', '--yes', '--pinentry-mode', 'loopback', '--passphrase-file', password_file, '-ab', jar_file_to_sign]
subprocess.run(sign_command, check=True)

# Step 5: Create checksums of the signature file
signature_file = jar_file_to_sign + '.asc'
checksum_sha1_command = ['sha1sum', signature_file, '>', signature_file + '.sha1']
checksum_md5_command = ['md5sum', signature_file, '>', signature_file + '.md5']

subprocess.run(' '.join(checksum_sha1_command), shell=True, check=True)
subprocess.run(' '.join(checksum_md5_command), shell=True, check=True)

print('Finished!')
