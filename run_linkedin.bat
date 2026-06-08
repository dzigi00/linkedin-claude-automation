@echo off
:: LinkedIn Daily Automation - Dzigi
:: Runs at 2:00 PM daily via Windows Task Scheduler

cd C:\Users\ivanz

echo Starting LinkedIn daily automation...
echo.

:: Run Claude Code - bypass permissions mode accepted via stdin
echo 2 | claude --dangerously-skip-permissions "Follow the instructions in C:\Users\ivanz\linkedin_daily.md exactly. Start from Step 1. Important: when asking Dzigi for a post idea, wait maximum 60 seconds for a response. If there is no response after 60 seconds, automatically generate a post yourself and continue."

pause