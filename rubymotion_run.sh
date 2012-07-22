#!/bin/sh

TERMINAL_ID="RubyMotionBuilder"
PROJECT_DIR="$1"
OPTIONS="$2"

if [ "${PROJECT_DIR}" = "" ]; then
    exit 1
fi

osascript<<END
try
    tell application "Terminal"
        activate
        try
            set buildWindow to item 1 of (every window whose custom title is "${TERMINAL_ID}")
            set index of buildWindow to 1
            do script "quit" in buildWindow
            do script "cd \"${PROJECT_DIR}\"" in buildWindow
        on error
            do script "alias quit='' && cd \"${PROJECT_DIR}\" && clear"
            tell window 1
                set custom title to "${TERMINAL_ID}"
            end tell
        end try
    delay 0.1
    do script "rake ${OPTIONS}" in front window
    end tell
end try
END