import docker
import os
import random
import tarfile

# Where all relevant files will be stored.
EXECUTION_FOLDER = "/tmp/{}"

# Relevant folder inside the Docker container.
CONTAINER_FOLDER = "/tmp/work"

# Names of files to be generated. 
TAR_FILE_NAME = "code.tar"
JAVA_CLASS_NAME = "Main"
CODE_FILE_NAME = JAVA_CLASS_NAME + ".java"

# The Docker image to use.
DOCKER_IMAGE = "oastem/virtualbot:latest"

DOCKER_CMD = "bash -c 'cd {0} && javac -cp ./VirtualBot.jar {1}.java && java -cp .:./VirtualBot.jar {1}'".format(CONTAINER_FOLDER, JAVA_CLASS_NAME)

# Docker client.
_client = docker.from_env()

# Generates a random alphanumeric string.
def _generate_string(length=8):
    dictionary = list(range(48, 58)) + list(range(65, 91)) + list(range(97,123))
    return "".join([chr(random.choice(dictionary)) for _ in range(length)])

# Runs the student-written code in a Docker container.
# code is a binary string.
def run_code(code):
    global _client
    # Generate a unique ID for this run.
    run_id = _generate_string()
    run_folder = EXECUTION_FOLDER.format(run_id)

    os.mkdir(run_folder)

    # First, we need to package the code into a tar file
    # that will be sent to the Docker container.
    
    with open(run_folder + "/" + CODE_FILE_NAME, 'wb') as code_fd:
        code_fd.write(code)

    with tarfile.TarFile(run_folder + "/" + TAR_FILE_NAME, 'w') as code_tar:
        code_tar.add(run_folder + "/" + CODE_FILE_NAME, arcname=CODE_FILE_NAME)

    # Now, create the Docker container and put the generated
    # tar file in.
    jvm_container = _client.containers.create(DOCKER_IMAGE, name=run_id, network_disabled=True, command=DOCKER_CMD)

    with open(run_folder + "/" + TAR_FILE_NAME, 'r') as code_tar_fd:
        code_tar_raw = code_tar_fd.read()

    jvm_container.put_archive(CONTAINER_FOLDER, code_tar_raw)

    jvm_container.start()

    return run_id

def wait(run_id):
    global _client
    try:
        jvm_container = _client.containers.get(run_id)
    except docker.errors.NotFound:
        return

    while jvm_container.status != "exited":
        jvm_container.reload()

def get_output(run_id):
    global _client
    try:
        jvm_container = _client.containers.get(run_id)
    except docker.errors.NotFound:
        return "Not found"

    return jvm_container.logs(stdout=True, stderr=True).decode('utf-8')

def remove(run_id):
    global _client
    try:
        jvm_container = _client.containers.get(run_id)
    except docker.errors.NotFound:
        return

    jvm_container.remove(force=True)
