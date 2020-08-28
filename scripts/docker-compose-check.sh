 #!/bin/sh
set -e
if command -v docker-compose /dev/null 2>&1; then
echo The command docker-compose is available
else
echo The command docker-compose is not available installing...
set -x
curl -L https://github.com/docker/compose/releases/download/1.25.3/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose     
fi   