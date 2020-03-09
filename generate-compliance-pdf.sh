#!/bin/sh
#
# This script generates a PDF of the compliance information that
# you can use to help fill out your GSA LATO paperwork.
#

# make sure we are in the correct directory
if [ ! -e compliance/Dockerfile ] || [ ! -e LICENSE ] ; then
	echo "You need to execute this from the root of the project"
	exit 1
fi

# make sure destination dir exists
mkdir -p compliance/exports/pdf

# make sure docker is running

if docker info >/dev/null 2>&1 ; then
	echo "Docker is running"
else
    echo "Docker does not seem to be running:  make sure that docker desktop is installed and running"
    exit 1
fi

# Build the latest docbook
if docker build -f compliance/Dockerfile . -t tanf-compliance ; then
	echo docker build succeeded
else
	echo docker build failed:  time to squash some bugs
	exit 1
fi

# build the PDF
docker run --rm -it --entrypoint="" -v "$(pwd)"/compliance/exports/pdf:/app/compliance/exports/pdf tanf-compliance gitbook pdf . ./pdf/tanf_compliance.pdf

# If we added the -w option to the commandline, then also up a webserverver
# with the documentation on port 4000
if [ "$1" = "-w" ] ; then
	echo starting up gitbook on http://localhost:4000/
	docker run --rm -i -t -p 4000:4000 tanf-compliance
fi

