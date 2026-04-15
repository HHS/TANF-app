#!/bin/bash

set -e

if [[ ! -x $(command -v godepgraph) ]]; then
    echo "godepgraph not found, skipping."
    exit 0
fi

if [[ ! -x $(command -v dot) ]]; then
    echo "dot not found, skipping."
    exit 0
fi

pushd $(dirname $0)

godepgraph -s -novendor -maxlevel 2 -p github.com,launchpad.net,golang.org ./internal/decoder | dot -Tpng -o decoder.png
godepgraph -s -novendor -maxlevel 2 -p github.com,launchpad.net,golang.org ./internal/config | dot -Tpng -o config.png
godepgraph -s -novendor -maxlevel 2 -p github.com,launchpad.net,golang.org ./internal/parser | dot -Tpng -o parser.png
godepgraph -s -novendor -maxlevel 2 -p github.com,launchpad.net,golang.org ./internal/pipeline | dot -Tpng -o pipeline.png
godepgraph -s -novendor -maxlevel 2 -p github.com,launchpad.net,golang.org ./internal/validation | dot -Tpng -o validation.png
godepgraph -s -novendor -maxlevel 2 -p github.com,launchpad.net,golang.org ./internal/writer | dot -Tpng -o writer.png

popd
