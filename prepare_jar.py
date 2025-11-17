import os
import subprocess
import re
import getpass
import glob
import shutil
import hashlib
from pathlib import Path

current_username = getpass.getuser()

# Resolve Ivy local root cross-platform; allow override via IVY2_LOCAL
_ivy_local_root = Path(os.environ.get("IVY2_LOCAL", str(Path.home() / ".ivy2" / "local")))
base_dir = str(_ivy_local_root / "com.microsoft.azure")


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
        try:
            os.rmdir(directory)
            print(f"Deleted: {directory}")
        except OSError as e:
            print(f"Warning: Could not delete {directory}: {e}")


# Normalize layout and filenames for all scala binary versions we publish
module_dirs = [
    d for d in os.listdir(base_dir)
    if d.startswith("onnx-protobuf_") and os.path.isdir(os.path.join(base_dir, d))
]

for module_dir in module_dirs:
    module_path = os.path.join(base_dir, module_dir)
    scala_suffix = module_dir.split("_", 1)[1] if "_" in module_dir else ""
    for version_dir in os.listdir(module_path):
        path_to_jars = os.path.join(module_path, version_dir)
        if not os.path.isdir(path_to_jars):
            continue
        flatten_dir(path_to_jars)

        # Ensure file names include the version suffix
        for file in os.listdir(path_to_jars):
            if f"_{scala_suffix}" in file and version_dir not in file:
                old_file_path = os.path.join(path_to_jars, file)
                name_parts = file.split(f"_{scala_suffix}")
                sep_char = "" if (len(name_parts) > 1 and (name_parts[1].startswith(".") or name_parts[1].startswith("-"))) else "-"
                new_file = f"{name_parts[0]}_{scala_suffix}-{version_dir}{sep_char}{name_parts[1] if len(name_parts) > 1 else ''}"
                new_file_path = os.path.join(path_to_jars, new_file)
                shutil.move(old_file_path, new_file_path)
                print(f"Renamed: {old_file_path} -> {new_file_path}")


def compute_digest(file_path, algorithm):
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def write_digest(file_path, algorithm):
    digest = compute_digest(file_path, algorithm)
    digest_path = f"{file_path}.{algorithm}"
    with open(digest_path, "w", encoding="utf-8") as handle:
        handle.write(digest + "\n")
    print(f"Wrote {algorithm} for {file_path}: {digest}")


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

# Step 3: Find all main jars (exclude -sources/-javadoc) across 2.12 and 2.13 modules
jar_files = []
for module_dir in module_dirs:
    module_path = os.path.join(base_dir, module_dir)
    candidates = glob.glob(os.path.join(module_path, '*', f'{module_dir}-*.jar'))
    for f in candidates:
        if ('-sources.jar' in f) or ('-javadoc.jar' in f):
            continue
        jar_files.append(f)

if not jar_files:
    raise Exception('Jar file(s) not found.')

# Step 4: Sign each jar and create checksums
for jar_file_to_sign in jar_files:
    print(f"signing jar: {jar_file_to_sign}")
    for ext in ['.sha1', '.md5', '.asc', '.asc.sha1', '.asc.md5']:
        try:
            os.remove(jar_file_to_sign + ext)
        except FileNotFoundError:
            print(f"Note: {jar_file_to_sign + ext} not found (skipping)")

    sign_command = ['gpg', '--batch', '--yes', '--pinentry-mode', 'loopback', '--passphrase-file', password_file, '-ab', jar_file_to_sign]
    subprocess.run(sign_command, check=True)

    for signature_file in [jar_file_to_sign, jar_file_to_sign + '.asc']:
        write_digest(signature_file, 'sha1')
        write_digest(signature_file, 'md5')

    print('Verify signature:')
    sign_command = ['gpg', '--verify', jar_file_to_sign + '.asc']
    subprocess.run(' '.join(sign_command), shell=True, check=True)


print('Finished!')
