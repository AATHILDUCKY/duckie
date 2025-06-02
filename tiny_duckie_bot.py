#!/usr/bin/env python3
import sqlite3
from typing import List, Dict
from search_algorithm import CommandSearcher
from colorama import init, Fore, Back, Style
import sys
import time
import os
import textwrap

init()  # Initialize Colorama

class TinyDuckieBot:
    def __init__(self, db_file: str = "hacker_commands.db"):
        self.db_file = db_file
        self.searcher = CommandSearcher()
        self._initialize_db()
        self._load_commands()
    
    def _initialize_db(self):
        """Initialize the SQLite database with commands table"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intent TEXT NOT NULL,
                    command TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT ''
                )
            """)
            conn.commit()
            
            # Add default commands if table is empty
            if cursor.execute("SELECT COUNT(*) FROM commands").fetchone()[0] == 0:
                default_commands = [
                    ("ssh connect with private key", "ssh username@host -i id_rsa", "Connect SSH using private key authentication"),
                    ("simple ssh command", "ssh username@host", "Basic SSH connection command"),
                    ("scan network ports", "nmap -sV -T4 192.168.1.0/24", "Scan network for open ports and services")
                ]
                cursor.executemany(
                    "INSERT INTO commands (intent, command, description) VALUES (?, ?, ?)",
                    default_commands
                )
                conn.commit()
    
    def _load_commands(self):
        """Load commands from database into the searcher"""
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM commands")
            commands = [dict(row) for row in cursor.fetchall()]
            self.searcher.build_index(commands)
    
    def search(self, query: str) -> list:
        """Search commands in the database"""
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM commands")
            all_commands = [dict(row) for row in cursor.fetchall()]
            return self.searcher.search(query, all_commands)
    
    def add_command(self, intent: str, command: str, description: str = "") -> bool:
        """Add a new command to the database"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO commands (intent, command, description) VALUES (?, ?, ?)",
                    (intent, command, description)
                )
                conn.commit()
            self._load_commands()  # Rebuild index
            return True
        except sqlite3.IntegrityError:  # Duplicate command
            return False
    
    def delete_command(self, command_id: int) -> bool:
        """Delete a command from the database by ID"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM commands WHERE id = ?", (command_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    self._load_commands()  # Rebuild index
                    return True
                return False
        except sqlite3.Error:
            return False
    
    def _format_command(self, command: str) -> str:
        """Format multi-line commands with proper indentation"""
        lines = command.split('\n')
        if len(lines) == 1:
            return command
        
        formatted_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                formatted_lines.append(line)
            else:
                formatted_lines.append(f"    {line.lstrip()}")
        return '\n'.join(formatted_lines)
    
    def _print_header(self):
        print(Fore.GREEN + r"""
   _____          _  __     __          _             _____       _ _    
  |_   _|        | | \ \   / /         | |           |  __ \     | | |   
    | | _ __  ___| | _\ \_/ /__  _   _| | _____ _ __| |  | | ___| | | __
    | || '_ \/ __| |/ /\   / _ \| | | | |/ / _ \ '__| |  | |/ _ \ | |/ /
   _| || | | \__ \   <  | | (_) | |_| |   <  __/ |  | |__| |  __/ |   < 
   \___/_| |_|___/_|\_\ |_|\___/ \__,_|_|\_\___|_|  |_____/ \___|_|_|\_\
                                                                         
        """ + Style.RESET_ALL)
        print(Fore.CYAN + " " * 20 + "🦆 The Quacktastic Hacker's Companion 🦆")
        print(Fore.YELLOW + " " * 25 + "Type /help for commands\n" + Style.RESET_ALL)
    
    def _print_help(self):
        print(Fore.MAGENTA + "\n[+] Available Commands:")
        print(Fore.YELLOW + "  /exit" + Fore.WHITE + " - Quit the DuckieBot")
        print(Fore.YELLOW + "  /add" + Fore.WHITE + " - Add new command (format: /add intent | command | [description])")
        print(Fore.YELLOW + "  /delete" + Fore.WHITE + " - Delete command by ID (format: /delete id)")
        print(Fore.YELLOW + "  /help" + Fore.WHITE + " - Show this help message")
        print(Style.RESET_ALL)
    
    def run(self):
        self._print_header()
        print(Fore.BLUE + "Initializing quackware..." + Style.RESET_ALL)
        time.sleep(0.5)
        
        print(Fore.GREEN + "\nHacker Command Assistant ready! (Type " + Fore.RED + "/exit" + Fore.GREEN + " to quit)" + Style.RESET_ALL)
        
        while True:
            try:
                user_input = input(Fore.CYAN + "\n🦆> " + Fore.WHITE).strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == '/exit':
                    print(Fore.RED + "\nQuacking off... See you soon, hacker duck!\n" + Style.RESET_ALL)
                    break
                
                if user_input.lower() == '/help':
                    self._print_help()
                    continue
                
                if user_input.lower().startswith('/add'):
                    parts = [p.strip() for p in user_input[4:].split('|')]
                    if len(parts) >= 2:
                        if self.add_command(parts[0], parts[1], parts[2] if len(parts) > 2 else ""):
                            print(Fore.GREEN + "✓ Command added to the duckie database!" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "⚠ Command already exists in the duckie pond!" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "Usage: /add intent | command | [description]" + Style.RESET_ALL)
                    continue
                
                if user_input.lower().startswith('/delete'):
                    try:
                        command_id = int(user_input[7:].strip())
                        if self.delete_command(command_id):
                            print(Fore.GREEN + f"✓ Command with ID {command_id} deleted from the duckie database!" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + f"⚠ No command found with ID {command_id} in the duckie pond!" + Style.RESET_ALL)
                    except ValueError:
                        print(Fore.RED + "Usage: /delete id (must be a number)" + Style.RESET_ALL)
                    continue
                
                print(Fore.YELLOW + f"\nSearching duckie database for '{user_input}'..." + Style.RESET_ALL)
                time.sleep(0.3)
                results = self.search(user_input)
                
                if not results:
                    print(Fore.RED + "\nNo matching commands found in the duckie pond. Try /add to contribute!" + Style.RESET_ALL)
                    continue
                
                # Show only the best match
                best_match = results[0]
                print(Fore.GREEN + f"\n🦆 Best Duckie Match ({best_match[1]:.0%} confidence):" + Style.RESET_ALL)
                print(Fore.CYAN + f"ID: " + Fore.WHITE + f"{best_match[0]['id']}")
                print(Fore.CYAN + f"Scenario: " + Fore.WHITE + f"{best_match[0]['intent']}")
                
                # Format the command with proper indentation
                formatted_command = self._format_command(best_match[0]['command'])
                print(Fore.CYAN + "Command: " + Style.RESET_ALL)
                print(Fore.YELLOW + textwrap.indent(formatted_command, '    ') + Style.RESET_ALL)
                
                if best_match[0]['description']:
                    print(Fore.CYAN + f"Details: " + Fore.WHITE + f"{best_match[0]['description']}")
                print(Style.RESET_ALL)
            
            except KeyboardInterrupt:
                print(Fore.RED + "\nUse /exit to quit the duckie console" + Style.RESET_ALL)
                continue

if __name__ == "__main__":
    bot = TinyDuckieBot()
    bot.run()
