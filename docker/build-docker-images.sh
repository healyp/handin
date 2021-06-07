#! /usr/bin/bash

delete_images="$1"

if [ ! -z "$delete_images" ]; then
  if [ "$delete_images" != "--delete" ]; then
    echo "Usage: docker/build_docker-images [--delete]"
    exit 1
  else
    delete_images="true"
  fi
else
  delete_images="false"
fi

files=$(find "$PWD"/docker -name "handin-*")

for f in $files; do
  f=$(basename $f)

  if [ "$delete_images" == "true" ]; then
    docker rmi -f "$f"

    status_code="$?"
    if [ "$status_code" -ne "0" ]; then
      echo -e "\nERROR: docker rmi exited with non-zero status code"
      exit $status_code
    fi
  else
    docker build -f "$PWD/docker/$f/Dockerfile" -t "$f" "$PWD/docker/$f"
    status_code="$?"
    if [ "$status_code" -ne "0" ]; then
      echo -e "\nERROR: docker build exited with non-zero status code"
      exit $status_code
    fi
  fi
done

if [ "$delete_images" == "true" ]; then
  echo -e "\nDocker images removed successfully"
else
  echo -e "\nDocker images built successfully"
fi

exit 0
