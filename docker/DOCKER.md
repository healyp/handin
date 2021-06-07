# Handin Docker Images
Docker is used by the handin system to execute a student's code that they submit.
This code is ultimately untrusted. The goal of the docker containers is to provide a
"sandbox" for the programs to be compiled and run in. 

## Requirements
- Docker (this has been tested on docker engine 20.10.6)
- epicbox 1.1.0 (pip install epicbox==1.1.0). This is the python library used to interact with
our docker containers from the server
- The user running the system_server needs to be in the docker group, this can be done with the
command: `sudo usermod -a -G docker <user>`
  
## Creating a docker image
To create a docker image for a new language, you need to follow steps to create the docker image
and also implement the language in src/handinexecutor/consts.py. Do the following:
- Inside the docker directory, create a directory called handin-<language-name>
- This directory name will become the name of the docker image, e.g. handin-gcc (used for c and c++)
, the image will be handin-gcc
- From an existing Dockerfile as an example, create a Dockerfile. There may be existing images
out there to base the Dockerfile off, like the way handin-python does `FROM python:3`. Google these
- See handin-gcc for examples of how to install the packages.
- The following lines must be in every Dockerfile used for handin:
```
RUN useradd -ms /bin/bash handin \
    && chown root:handin /home/handin \
    && chmod 1775 /home/handin
```
- As the last (or second last line if following the next line) line, put:
  `WORKDIR /home/handin`
- To interact with the docker container outside the system_server (see later), you'll
need to include the following line at the end:
  `CMD [ "/bin/bash" ]`
- In src/handinexecutor/handin_executor.py, you will need to add profiles and extra supported languages
to the file. In PROFILES, add an entry \<language>_compile (see other compile for examples)
  if the language needs to be compiled, and an entry \<language>_run with user handin (see other run for examples):
  example, c and c++ use gcc or g++, so profiles are setup as so:
  ```
  PROFILES = {
    'gcc_compile': {
        'docker_image': 'handin-gcc',
        'user': 'root',
    },
    'gcc_run': {
        'docker_image': 'handin-gcc',
        'user': 'handin',
        'network_disabled': True,
    },
    ... other profiles
  }
  ```
- Add the language to supported languages:
```
SUPPORTED_LANGUAGES = ["python", "java", "c", "c++", "lua"]
```
- Add an entry to the LANGUAGE_PROFILES also. For compiled programs, keep the compile profile to
the left of the list and run to the right:
```
LANGUAGE_PROFILES = {
    "gcc": ["gcc_compile", "gcc_run"],
    "python": ["python_run"],
    "java": ["java_compile", "java_run"],
    "lua": ["lua_run"]
}
```
- Add an entry to the FILE_EXTENSION_MAPPINGS:

```
FILE_EXTENSION_MAPPINGS = {
    "py": "python",
    "pyo": "python",
    "pyc": "python",
    "java": "java",
    "c": "c",
    "cc": "c++",
    "cpp": "c++",
    "lua": "lua"
}
```
- Add an entry for the language and its respective image to the LANGUAGE_IMAGE_MAPPINGS map. If the same image is used for more than
1 language, enter the 2 languages pointing to the same image:
```
LANGUAGE_IMAGE_MAPPINGS = {
    "c": "handin-gcc",
    "c++": "handin-gcc",
    "python": "handin-python",
    "java": "handin-java",
    "lua": "handin-lua"
}
```
- If 2 languages can be run by the same container (e.g. c and c++), you may need to 
modify the _Executor._deduce_language method in consts. For example, it has the line for c and c++:
```
    if language == "c" or language == "c++":
      return "gcc"
    else:
      return language
```

## Building the docker images
To build the docker images, run the script docker/build-docker-images.sh (from the root of the project)
To build an individual container, run the following command:
`docker build -f docker/handin-<language>/Dockerfile -t handin-<language> docker/handin-<language>`

gcc example:

`docker build -f docker/handin-gcc/Dockerfile -t handin-gcc docker/handin-gcc`

Again, the user running this script/command needs to be a member of the docker group.

If it's the first build, this can take some time. However, if the build is done to just update
an image, it should be much quicker

## Running the docker image
After the docker images have been built, they are ready to go as long as the system_server is
running. However, if you want to interact with a container on the command line (you need to have added 
the CMD line to the Dockerfile, see Creating a docker image), you can follow these steps:
- The user needs to be in the docker group
- Run the command `docker run --rm -it --name handin-<language> handin-<language>`
- GCC example `docker run --rm -it --name handin-gcc handin-gcc`
- On success of this command, you should now be brought into a bash shell on the docker container

## Docker image libraries
If you need specific libraries (for example with C/C++), you need to set them up to be installed
in the Dockerfile and re-build the image. Since the gcc docker image is based on Ubuntu 18.04, 
you can use apt-get with the following lines:
```
RUN apt-get -y update && apt-get -y install \
                    software-properties-common \
                   && add-apt-repository ppa:deadsnakes/ppa \
                   && apt-get -y install \ # list packages here. These packages are examples
                        g++ \
                        freeglut3-dev \
                        libglu1-mesa-dev \
                        mesa-common-dev \
                        libomp-dev && rm -rf /var/lib/apt/lists/*
```