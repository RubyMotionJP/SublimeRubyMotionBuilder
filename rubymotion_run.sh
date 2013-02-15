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
						close (every window whose custom title is "${TERMINAL_ID}")
						close (every window whose custom title is "rake")
	          do script "cd \"${PROJECT_DIR}\""

				on error errs number errn
						display dialog errs & return & "Error: " & (errn as string)
            do script "alias quit='' && cd \"${PROJECT_DIR}\" && clear"
        end try
    		
				delay 0.1

		    tell window 1
		        set custom title to "${TERMINAL_ID}"
		    end tell

		    do script "rake ${OPTIONS}" in front window
	    end tell
end try
END