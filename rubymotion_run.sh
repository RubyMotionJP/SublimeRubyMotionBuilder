#!/bin/sh

TERMINAL_APP="$1"
ACTIVATE_TERMINAL="$2"
PROJECT_DIR="$3"
OPTIONS="$4"

if [ "${PROJECT_DIR}" = "" ]; then
    exit 1
fi

if [ "${OPTIONS}" = "" ]; then
    RAKE="rake"
else
    RAKE="rake ${OPTIONS}"
fi
if type bundle >/dev/null 2>&1; then
    if [ -f "Gemfile" ]; then
        RAKE="bundle exec ${RAKE}"
    fi
fi

if [ "${TERMINAL_APP}" = "iTerm" ]; then
    osascript<<END
        tell application "iTerm"
            if "${ACTIVATE_TERMINAL}" is "true" then activate
            set current_session to (the first session of the current terminal)
            select current_session

            tell current_session
                if ("ruby" is in name or "rake" is in name or "sim" is in name) then 
                    write text "exit"
                end if

                write text "cd '${PROJECT_DIR}'"
                write text "${RAKE}"
            end tell
        end tell
END
else
    osascript<<END
        tell application "Terminal"
            if "${ACTIVATE_TERMINAL}" is "true" then activate
            try
                set buildWindow to window 1
                set selected tab of buildWindow to tab 1 of buildWindow
                if (processes in buildWindow) contains "sim" then
                    do script "exit" in buildWindow
                end if
                do script "cd '${PROJECT_DIR}'" in buildWindow
            on error
                do script "alias exit='' && cd '${PROJECT_DIR}' && clear"
                delay 0.5
            end try
            do script "${RAKE}" in front window
        end tell
END
fi
