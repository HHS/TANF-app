 #!/bin/sh
set -e
if command -v docker /dev/null 2>&1; then
echo The command docker is available
else
echo The command docker is not available installing...
set -x
VER="17.03.0-ce"
curl -L -o /tmp/docker-$VER.tgz https://get.docker.com/builds/Linux/x86_64/docker-$VER.tgz
tar -xz -C /tmp -f /tmp/docker-$VER.tgz
mv /tmp/docker/* /usr/bin
fi  