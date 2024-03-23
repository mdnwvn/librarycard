# Library Card 3.3.1

## A dragon-themed discord group reading completion and suggestion tracker with book index summary information retrieval
Wow thats a lot of keywords


# Usage

### Creating the Bot

Also known as _"how do I get a token?"_

0. Go to [your applications][discord-apps] (you'll need to be logged in to
   Discord)
1. Create a "New Applications"
2. Go ahead and give it a name and icon in General Information, it won't bite.
   Save your changes.
3. **IMPORTANT**: In "Installation", under "Install Link", choose "Discord
   Provided Link." This will also open up "Default Install Settings," in which
   you _must_ add `bot` to "Scopes". Save your changes.
4. **ALSO IMPORTANT**: Go to "Bot". Under "Build-a-bot", "Token", click "Reset
   Token". Authenticate as needed, and you'll be provided with a token. _Copy
   this immediately to a safe place_, you'll need this for the application
   setup.
5. **IMPORTANT AS WELL**: Still in "Bot", under "Privileged Gateway Intents",
   turn on "Message Content Intent". Save your changes.
6. Go back to "Installation". Copy that link, and open it in a browser where
   you're logged in (the same one you're making the app from will do). You can
   add it to any Guild/Server for which you are an administrator. (If nothing's
   copacetic, it's not hard to create a server--go to the bottom of your server
   sidebar and find the "+" button.)

The bot user won't do anything until you run the application, of course.
Proceed below.


[discord-apps]: https://discord.com/developers/applications

### Setup
0. Clone the repo.
1. Copy `.example.env` into `.env` and configure it in your favorite text
   editor
   - You'll need that token above for `TOKEN`.
   - Follow the instructions for `MONGO_STRING`: if you're setting up with
     Docker Compose, you don't need to specify this. Otherwise, you'll need to
     run an unauthenticated MongoDB somewhere _secure_ and point this at it.
2. [Run the darn thing.](#ways-to-run)
3. ????
4. Profit

#### Ways to Run

Depending on your preferences and scale, you can run the bot a few different
ways.

##### Docker-Compose

This way is most suitable for itinerant development--bug fixes, features, and
the like.

In the repo root, do

```
docker-compose build
docker-compose up -d
```

That's it. The containers are `restart: unless-stopped`, so they'll come up
following your Docker service restarting (say, on a reboot).

Stop it with

```
docker-compose down
```

in the repo root if you need to.

##### Self Hosted on Linux with Dedicated User and Systemd

This way is most suitable for long-running, production installations.

First, add that user account:

```
# CHOOSE ONE:
adduser librarycard  # Debian-based, including Ubuntu-based
useradd -m librarycard  # Just about everywhere
```

Become that user (you'll need to be an administrator):

```
sudo -iu librarycard
```

Either clone this repo or (perhaps as root) move the repo into this user's
home. The latter involves fixing permissions; if you're not comfortable with
that, cloning is easier. Make sure you include your local changes, especially
the `.env` file.

When you've done that, `cd` into the repo. You know where you put it better
than I do, so I can't give the exact command.

Python _highly_ recommends using a Virtual Environment to namespace installed
Python modules. You can make one and install the modules with:

```
python -m venv .venv
. .venv/bin/activate
pip -r requirements.txt
```

(Some Debians may need you to install a package like `python3-venv` as root; do
so if you need to.)

If you're not into package isolation, you can also just do

```
pip -r requirements.txt
```

as root. This can and will break other apps on your system, so be careful.

While you're root, copy `librarycard.service` to `/etc/systemd/system`. Then

```
systemctl daemon-reload
systemctl enable --now librarycard.service
```

It should now be running, and will start on boot.

Stop it with

```
systemctl stop librarycard.service
```

if you need to.

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
