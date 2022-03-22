#!/bin/bash

DOCROOT="$(dirname "$(readlink -f "$0")")"
BUILDROOT="$DOCROOT/generated"

echo
echo 'Building agave docs'
echo
mkdir -p "$BUILDROOT"
rm -r "$BUILDROOT" 2>/dev/null || true
pushd "$DOCROOT/.." >/dev/null
pdoc3 --html \
     --output-dir "$BUILDROOT" \
     agave
popd >/dev/null

echo
echo "All good. Docs in: $BUILDROOT"
echo
echo "    file://$BUILDROOT/agave/index.html"
echo