#!/bin/sh

TERMINAL_ID="RubyMotionBuilder"
TERMINAL_APP="$1"
PROJECT_DIR="$2"
OPTIONS="$3"

if [ "${PROJECT_DIR}" = "" ]; then
    exit 1
fi

if [ "${OPTIONS}" = "" ]; then
    RAKE="rake"
else
    RAKE="rake ${OPTIONS}"
fi

if [ "${TERMINAL_APP}" = "iTerm" ]; then
    osascript<<END
        tell application "iTerm"
            activate
            set current_session to (the first session of the current terminal)

            tell current_session
                if ("rake" is in name of current_session) then write text "exit"

                write text "cd ${PROJECT_DIR}"
                write text "${RAKE}"
            end tell
        end tell
END
else
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
            do script "${RAKE}" in front window
            end tell
        end try
END
fi
