#!/bin/bash
#
# Download the complete archive of text format files from Project Gutenberg.
# This script will pick up from
# where it left off if it fails or is stopped.
#
 
# ------------------------------------------------------------------------
# Preliminaries
# ------------------------------------------------------------------------
 
set -o nounset
set -o errexit
 
# Restrict downloads to this file format.
FORMAT=txt
# Restrict downloads to this language.
LANG=en
 
# The directory in which this file exists.
DIR="$( cd "$( dirname "$0" )" && pwd)"
# File containing the list of zipfile URLs.
ZIP_LIST="${DIR}/zipfileLinks.txt"
# A subdirectory in which to store the zipfiles.
ZIP_DIR="${DIR}/zipfiles"
# A directory in which to store the unzipped files.
UNZIP_DIR="${DIR}/files"

# ------------------------------------------------------------------------
# Unzip the zipfiles.
# ------------------------------------------------------------------------
 
echo "-------------------------------------------------------------------------"
echo "Unzipping files."
echo "-------------------------------------------------------------------------"
 
for ZIP_FILE in $(find ${ZIP_DIR} -name '*.zip')
do
  UNZIP_FILE=$(basename ${ZIP_FILE} .zip)
  UNZIP_FILE="${UNZIP_DIR}/${UNZIP_FILE}.txt"
  # Only unzip if not already unzipped. This check assumes that x.zip unzips to
  # x.txt, which so far seems to be the case.
  if [ ! -f "${UNZIP_FILE}" ] ; then
    unzip -o "${ZIP_FILE}" -d "${UNZIP_DIR}"
  else
    echo "${ZIP_FILE##*/} already unzipped. Skipping."
  fi
done
