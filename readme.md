# Library Card 3.2.0

## A dragon-themed discord group reading completion and suggestion tracker with book index summary information retrieval
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

- `/start-session` to start a reading session.
- `/end-session` to end a reading session.
- `/draw-nominees [min_nominations: optional (default 2), [past_sessions: optional (default 0)` to select the nominees from the current reading session that have at least the required nomination count. min_nominations will always consider 2 or more (number informed by the user). Use past_sessions to include nominations from previous sessions.
  
Everyone can:
- `/library` to list everything in your Flight's library  
- `/leaderboard` to see who's hoard is largest  
- `/hoard [user: optional]` to view your hoard or another's.  
- `/readbook` to read a book in the library and add it to your hoard  
- `/forgetbook` to forget a book and remove it from your hoard  
- `/unopened` to check out what you haven't read yet

- `/nominate` to nominates a book to the current active reading session. Book title required.
- `/list-nominations [past_sessions: optional (default 0)]` to list all nominated books for the current active session by all users. Use past_sessions to include nominations from previous sessions.

***

Its not a perfect bot, given it was originally written in an afternoon, but it should be functional.
