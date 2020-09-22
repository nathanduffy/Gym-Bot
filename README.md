# Gym-Bot
Gym-Bot is a bot used to check stock availability of certain items at either Rep Fitness or Rogue Fitness

# Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
pip install requirements.txt 
```

# Setup
Add specific items you wish to track inside 'ROGUE_ITEMS_TO_WATCH' or 'REP_ITEMS_TO_WATCH'

# Usage
setup a chron job to periodically check stock availability of certain items
```bash
sh setupCron.sh
```
You can also tear down the cron when you want to stop running it
```bash
sh stopCron.sh
```
