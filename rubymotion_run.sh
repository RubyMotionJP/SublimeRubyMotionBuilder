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
						close (every window whose custom title is "rake")
						delay 0.5
		        do script "cd \"${PROJECT_DIR}\""
				    do script "rake ${OPTIONS}" in front window
				on error errs number errn
						display dialog errs & return & "Error: " & (errn as string)
        end try
	    end tell
end try
END