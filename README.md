# LinkedIn Claude Automation

Full LinkedIn growth automation using Claude Code and a custom LinkedIn MCP server. Runs daily via Windows Task Scheduler with zero manual interaction required.

## What it does

Every day at 2pm automatically:
- Checks your LinkedIn inbox and replies to messages in In English (Serbian also supported)
- Relevant, high-quality and human-feeling posts
- Sends 7 to 8 personalized connection requests
- Tracks your connection count growth daily
- Prints a full session report

On Monday, Wednesday, and Friday it also:
- Asks you for a post idea (60 second window)
- Auto-generates and publishes a post in your voice if you don't respond

## How it works

This project extends the [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server) package by adding two missing tools:
- `create_post` - publishes a post to your LinkedIn profile
- `comment_on_post` - leaves a comment on any LinkedIn post

These tools use browser automation (Patchright/Chromium) to interact with LinkedIn's UI directly.

Claude Code reads a prompt file (`linkedin_daily.md`) that contains detailed instructions for the daily automation. Windows Task Scheduler fires the bat file at 2pm every day.

## Requirements

- Windows PC (always on during automation time)
- [Claude Code](https://claude.ai/code) installed
- [UV](https://astral.sh/uv) installed
- Claude Pro or API access

## Setup

### 1. Install UV

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and install the custom MCP

```powershell
git clone https://github.com/dzigi00/linkedin-claude-automation C:\Users\<you>\linkedin-mcp-custom
cd C:\Users\<you>\linkedin-mcp-custom
uv sync
```

### 3. Login to LinkedIn

```powershell
uv run -m linkedin_mcp_server --login
```

A browser opens. Log in to your LinkedIn account. Session is saved automatically.

### 4. Register the MCP with Claude Code

```powershell
claude mcp add linkedin -s user -- "C:\Users\<you>\.local\bin\uv.exe" "--directory" "C:\Users\<you>\linkedin-mcp-custom" "run" "-m" "linkedin_mcp_server" "--transport" "stdio"
```

### 5. Copy the automation files

Copy `linkedin_daily.md` and `run_linkedin.bat` to `C:\Users\<you>\`

Edit `linkedin_daily.md` to match your profile, niche, and content topics.

Edit `run_linkedin.bat` to replace the path with your actual username.

### 6. Schedule with Windows Task Scheduler

- Open Task Scheduler
- Create Basic Task
- Name: LinkedIn Daily
- Trigger: Daily at 2:00 PM
- Action: Start a program
- Program: `C:\Users\<you>\run_linkedin.bat`
- Start in: `C:\Users\<you>`

## Files

- `linkedin_mcp_server/tools/posting.py` - custom create_post and comment_on_post tools
- `linkedin_daily.md` - daily automation prompt instructions
- `run_linkedin.bat` - Windows Task Scheduler script

## Credit

Built on top of [stickerdaniel/linkedin-mcp-server](https://github.com/stickerdaniel/linkedin-mcp-server). This project adds write capabilities (posting and commenting) that the original package does not include.

## License

MIT
