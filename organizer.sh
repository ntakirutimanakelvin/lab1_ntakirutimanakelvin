#!/bin/bash
#
# organizer.sh
# Archives the current grades.csv (with a timestamp), resets the workspace
# with a fresh empty grades.csv, and logs every run to organizer.log.

ARCHIVE_DIR="archive"
SOURCE_FILE="grades.csv"
LOG_FILE="organizer.log"

# 1. Make sure the archive directory exists
if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir "$ARCHIVE_DIR"
    echo "Created archive directory: $ARCHIVE_DIR"
fi

# 2. Make sure there is something to archive
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: '$SOURCE_FILE' not found in the current directory. Nothing to archive."
    exit 1
fi

# 3. Generate a timestamp for this run
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# 4. Build the archived filename and move the file into archive/
ARCHIVED_NAME="grades_${TIMESTAMP}.csv"
mv "$SOURCE_FILE" "$ARCHIVE_DIR/$ARCHIVED_NAME"

# 5. Reset the workspace: create a fresh, empty grades.csv
touch "$SOURCE_FILE"

# 6. Log the operation (append, so history accumulates across runs)
echo "$(date +"%Y-%m-%d %H:%M:%S") | original=$SOURCE_FILE | archived_as=$ARCHIVE_DIR/$ARCHIVED_NAME" >> "$LOG_FILE"

echo "Archived '$SOURCE_FILE' as '$ARCHIVE_DIR/$ARCHIVED_NAME'."
echo "A fresh, empty '$SOURCE_FILE' has been created."
echo "Run details logged to '$LOG_FILE'."
