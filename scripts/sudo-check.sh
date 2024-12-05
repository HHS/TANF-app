 #!/bin/sh
set -e
if command -v sudo /dev/null 2>&1; then
    echo The command sudo is available
else
    echo The command sudo is not available installing...
    if [ -f /bin/terraform ]; then
        echo "This is our Terraform executor, Alpine Linux v3.13"
        apk update
        apk add sudo
    else
        apt-get update && apt-get install -y sudo
    fi
    ls -al /bin/sh && sudo rm /bin/sh && sudo ln -s /bin/bash /bin/sh && ls -al /bin/sh
fi  