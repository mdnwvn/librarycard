# Library Card

## A dragon-themed discord group reading completion tracker
Wow thats a lot of keywords


# Usage

### Shopping List
- MongoDB
- Python
- Discord Bot Token

### Setup
1. Copy `.example.env` into `.env`
2. Configure your Discord token and MongoDB connection string
3. Run `librarycard.py`
4. ????
5. Profit

### Actually Using It

`manage-messages` permission is needed for:
  - `/addbook` to add your first book to the library. Book title required.
  - `/delbook` to destroy a book to the library. Book title required.
  
Everyone can:
  - `/listbooks` to list everything in your Flight's library
  - `/leaderboard` to see who's hoard is largest
  - `/hoard` to view your hoard, optionally supply another user to view theirs.
  - `/readbook` to read a book in the library and add it to your hoard
  - `/forgetbook` to forget a book and remove it from your hoard


***

Its not a perfect bot, given I wrote it in an afternoon, but it should be functional.