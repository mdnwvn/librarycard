# Library Card 2.3.3

## A dragon-themed discord group reading completion tracker
Wow thats a lot of keywords


# Usage

### Shopping List
- MongoDB
- Python
- Discord Bot Token

### Setup
0. Clone the repo into `/opt/librarycard` (No Windows instructions in this lair)
1. Copy `.example.env` into `.env`
2. Configure your Discord token and MongoDB connection string
3. 
    - Run `librarycard.py` OR:
    - Create a `librarycard` user account
    - Install the Unit file into `/etc/systemd/system/librarycard.service`
    - Enable and start with `systemctl enable --now librarycard`
4. ????
5. Profit

### Actually Using It

`manage-messages` permission is needed for:
  - `/addbook` to add your first book to the library. Book title required.
  - `/delbook` to destroy a book to the library. Book title required.
  
Everyone can:
- `/library` to list everything in your Flight's library  
- `/leaderboard` to see who's hoard is largest  
- `/hoard [user: optional]` to view your hoard or another's.  
- `/readbook` to read a book in the library and add it to your hoard  
- `/forgetbook` to forget a book and remove it from your hoard  


***

Its not a perfect bot, given I wrote it in an afternoon, but it should be functional.