# TinyDuckieBot 🦆

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

The Quacktastic Hacker's Companion - A CLI tool to help you remember and organize your hacking commands with fuzzy search capabilities.

![TinyDuckieBot Demo](demo.gif) *Example usage*

```
└─$ duckie    

   _____          _  __     __          _             _____       _ _    
  |_   _|        | | \ \   / /         | |           |  __ \     | | |   
    | | _ __  ___| | _\ \_/ /__  _   _| | _____ _ __| |  | | ___| | | __
    | || '_ \/ __| |/ /\   / _ \| | | | |/ / _ \ '__| |  | |/ _ \ | |/ /
   _| || | | \__ \   <  | | (_) | |_| |   <  __/ |  | |__| |  __/ |   < 
   \___/_| |_|___/_|\_\ |_|\___/ \__,_|_|\_\___|_|  |_____/ \___|_|_|\_\
                                                                         
        
                    🦆 The Quacktastic Hacker's Companion 🦆
                         Type /help for commands

Initializing quackware...

Hacker Command Assistant ready! (Type /exit to quit)

🦆> nmap privilege es

Searching duckie database for 'nmap privilege es'...

🦆 Best Duckie Match (92% confidence):
ID: 23
Scenario: privilege escalation with nmap
Command: 
    nmap --interactive \n nmap>!sh
Details: privilege escalation with nmap, i want to use nmap sudo file for pri

```



## Features ✨

- **Fuzzy Command Search**: Find commands even with partial or mistyped queries
- **Command Storage**: Save your favorite commands with descriptions
- **Interactive CLI**: Colorful duck-themed interface
- **Multi-line Commands**: Supports complex commands with proper formatting
- **Easy Management**: Add, delete, and search commands with simple syntax

## Installation 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tiny-duckie-bot.git
   cd tiny-duckie-bot
   ```
2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```
3. Make the script executable (optional):
   ```
   chmod +x tiny_duckie_bot.py
   ```

## Usage 🚀

Run the bot:
```
python tiny_duckie_bot.py
```

### Basic Commands

| Command          | Description                                      | Example                          |
|------------------|--------------------------------------------------|----------------------------------|
| `/exit`          | Quit the bot                                     | `/exit`                          |
| `/help`          | Show help message                                | `/help`                          |
| `/add`           | Add new command                                  | `/add ssh connect \| ssh user@host` |
| `/delete`        | Delete command by ID                             | `/delete 3`                      |
| `[search term]`  | Search for commands matching your query          | `nmap scan`                      |


## Adding Commands

Use the /add command with the following format:

```
/add intent | command | [description]
```

Example:
```
/add port scan | nmap -sV -T4 192.168.1.0/24 | Scan network for open ports
```

## Database Structure 💾

Commands are stored in an SQLite database ``hacker_commands.db`` with the following schema:

```
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent TEXT NOT NULL,
    command TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT ''
)
```

## Dependencies 📦

- Python 3.7+
- colorama - For colored terminal output
- sqlite3 - Built-in Python module for database operations

## Contributing 🤝

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.






