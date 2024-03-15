import discord
import lib.goodreads as goodreads
import os
from dotenv import load_dotenv
import typing
import pymongo
from bson.objectid import ObjectId
import math
from discord.ext.pages import Paginator
from pymongo import TEXT
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
from discord import Option, default_permissions
from discord import guild_only


load_dotenv()

client = pymongo.MongoClient(os.getenv('MONGO_STRING'))
books = client.librarycard.books

books.create_index([('name', TEXT)])
books.create_index([('guild', ASCENDING)])
books.create_index([('readers.user', ASCENDING)])

nominateSessions = client.librarycard.nominateSessions

nominateSessions.create_index([('guild', ASCENDING)])
nominateSessions.create_index([('nominations.name', ASCENDING)])

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

@bot.slash_command(name="addbook", description = "Add a book to your Flight's library")
@guild_only()
@default_permissions(manage_messages=True)
async def addBook(ctx, book: str):

  search = {
    'name': book,
    'guild': ctx.guild.id,
  }
  found = books.find(search).limit(10)

  count = 0
  for d in found:
    count += 1
  if count > 0:
    await ctx.respond('Identical book exists already')
    return

    
  document = {
    'name': book.strip(),
    'guild': ctx.guild.id,
    'added': datetime.now(),
    'readers': []
  }
  result = books.insert_one(document)
  if (result.inserted_id): 
    await ctx.respond(f'***{book}*** added to library')
  else:
    await ctx.respond('Failed to add book to library')

@bot.slash_command(name="delbook", description = "Remove a book from your Flight's library")
@guild_only()
@default_permissions(manage_messages=True)
async def delBook(ctx, book: str):

  search = {
    'name': book,
    'guild': ctx.guild.id,
  }
  projection ={
    'readers': 0
  }
  found = books.find(search, projection).limit(25)

  foundBooks = []

  count = 0
  for d in found:
    foundBooks.append(d)
    count += 1

  if count < 1:
    await ctx.respond('Book not found')
    return

  if count > 1:
    
    embed = discord.Embed(title="Error: Book Conflict", description="Please use `delbookbyid` instead.")
    embed.add_field(name="[Book Id]", value="[Book Name]", inline=False)
    for b in foundBooks:
      embed.add_field(name=b['_id'], value=b['name'], inline=False)
    await ctx.respond(embed=embed)
    return

  result = books.delete_one(search)
  if result.acknowledged:
    await ctx.respond('Book deleted')
  else:
    await ctx.respond('Book not deleted')

@bot.slash_command(name="delbookbyid", description = "Remove a book from your Flight's library")
@guild_only()
@default_permissions(manage_messages=True)
async def delBookById(ctx, id: str):

  search = {
    "_id": ObjectId(id),
    'guild': ctx.guild.id,
  }
  result = books.delete_one(search)
  if result.acknowledged:
    await ctx.respond('Book deleted')
  else:
    await ctx.respond('Book not deleted')

@bot.slash_command(name="library", description = "List all the book in your Flight's library")
@guild_only()
async def library(ctx):

  count = books.count_documents({'guild': ctx.guild.id})
  pagecount = math.ceil((count/10))

  pages = []

  for p in range(pagecount):
    search = {
      'guild': ctx.guild.id
    }
    found = books.find(search).sort([('added', DESCENDING)]).limit(10).skip((p) * 10)

    embed = discord.Embed(title="Book listing", description= str(count) + " books in the library.")
    for b in found:
      embed.add_field(name=b['name'], value='Readers: ' + str(len(b['readers'])), inline=False)
    
    pages.append(embed)
  
  if len(pages) == 0:
    await ctx.respond('Library Empty')
    return

  pagination = Paginator(pages=pages)
  await pagination.respond(ctx.interaction, ephemeral=True)

@bot.slash_command(name="unopened", description = "List all the books you haven't read yet")
@guild_only()
async def unopened(ctx):
  

  countpipeline = [ 

    { '$match': {
    'guild': ctx.guild.id,
    }}, {
      '$project': {

      'name': {'$toLower':"$name"},
      'hasread': {
        '$in': [
          ctx.author.id, "$readers.user"
        ]
      },
      
      }
    },
    {
      '$match': {
        'hasread': False
      }
    }, {
        '$group': {
            '_id': 'counter', 
            'count': {
                '$count': {}
            }
        }
    }

  ]
  

  countagg = books.aggregate(countpipeline)

  crp = {}
  for l in countagg:
    crp = l

  pagecount = math.ceil((int(crp['count'])/10))

  pages = []

  for p in range(pagecount):
    searchPipeline = [ 

    { '$match': {
    'guild': ctx.guild.id,
    }}, 
    {
        '$sort': {
          'added': -1
        }
      },
      {
      '$project': {

      'name': "$name",
      'hasread': {
        '$in': [
          ctx.author.id, "$readers.user"
        ]
      },
      
      }
    },
    {
      '$match': {
        'hasread': False
      }
    },
      {
        '$skip': p * 10
      },
      {
        '$limit' : 10
      }

  ]
    found = books.aggregate(searchPipeline)

    embed = discord.Embed(title="Book listing", description= str(crp['count']) + " books left.")
    for b in found:
      embed.add_field(name=b['name'], value='', inline=False)
    
    pages.append(embed)
  
  if len(pages) == 0:
    await ctx.respond('You\'ve read it all')
    return

  pagination = Paginator(pages=pages)
  await pagination.respond(ctx.interaction, ephemeral=True)


@bot.slash_command(name="readbook", description="Read a book and add it to your hoard")
@guild_only()
async def readBook(ctx, book: str):
  searchpipeline = [ 
    { '$match': {
    'guild': ctx.guild.id,
    }}, {
      '$project': {

      'name': {'$toLower':"$name"},
      
      }
    },
    {
      '$match': {
        'name': book.lower()
      }
    }

  ]

  found = books.aggregate(searchpipeline)

  foundBooks = []
  foundbook = {}

  count = 0
  for d in found:
    foundBooks.append(d)
    foundbook = d
    count += 1

  if count < 1:
    await ctx.respond('Book not found', ephemeral=True)
    return

  if count > 1:
    
    embed = discord.Embed(title="Error: Book Conflict", description="Please use `readbookbyid` instead.")
    embed.add_field(name="[Book Id]", value="[Book Name]", inline=False)
    for b in foundBooks:
      embed.add_field(name=b['_id'], value=b['name'], inline=False)
    await ctx.respond(embed=embed)
    return


  existingsearchpipeline = [ 
    { '$match': {
    'guild': ctx.guild.id,
    'readers.user': ctx.author.id,
    }}, {
      '$project': {

      'name': {'$toLower':"$name"},
      
      }
    },
    {
      '$match': {
        'name': book.lower()
      }
    }

  ]

  foundexisting = books.aggregate(existingsearchpipeline)

  

  existingcount = 0
  for d in foundexisting:
    existingcount += 1
  
  if existingcount > 0:
    await ctx.respond('Already hoarded this book', ephemeral=True)
    return

  search = {
    '_id': foundbook['_id'],
    'guild': ctx.guild.id,
  }

  readerobject = {
    'read': datetime.now(),
    'user': ctx.author.id,
    'guild': ctx.guild.id,
  }
  result = books.update_one(search, {
    '$push': {
      'readers': readerobject
    }
  })

  if result.acknowledged:
    await ctx.respond(f'{book} added to hoard')
  else: 
    await ctx.respond('Book could not be added to hoard')


@bot.slash_command(name="forgetbook", description="Forget about a book and remove it from your hoard")
@guild_only()
async def forgetBook(ctx, book:str):
  existingsearchpipeline = [ 
    { '$match': {
    'guild': ctx.guild.id,
    'readers.user': ctx.author.id,
    }}, {
      '$project': {

      'name': {'$toLower':"$name"},
      
      }
    },
    {
      '$match': {
        'name': book.lower()
      }
    }

  ]

  foundexisting = books.aggregate(existingsearchpipeline)

  existing = []
  existingbook = {}

  existingcount = 0
  for d in foundexisting:
    existing.append(d)
    existingbook = d
    existingcount += 1
  
  if existingcount == 0:
    await ctx.respond('You have nothing to forget')
    return
  if existingcount > 1:
    embed = discord.Embed(title="Error: Book Conflict", description="Please use `forgetbookbyid` instead.")
    embed.add_field(name="[Book Id]", value="[Book Name]", inline=False)
    for b in existing:
      embed.add_field(name=b['_id'], value=b['name'], inline=False)
    await ctx.respond(embed=embed)
    return

  search = { '_id': existingbook['_id'],'guild': ctx.guild.id,}
  update = {
          '$pull': {
            'readers': {
              'user': ctx.author.id
            }
          }
        }
        
  
  result = books.update_one(search, update)


  if result.acknowledged:
    await ctx.respond('You forgot about ' + book)
  else: 
    await ctx.respond('You\'re bad at forgetting')


@bot.slash_command(name="hoard", description="Check out your (or a wingmate's) hoard")
@guild_only()
async def hoard(ctx, user: typing.Optional[discord.Member]):

  userid = ctx.author.id
  username = ctx.author.name
  ephem = True

  if user:
    userid = user.id
    username = user.name
    ephem = False


  search = {
      'guild': ctx.guild.id,
      'readers.user': userid,
      }

  count = books.count_documents(search)
  pagecount = math.ceil((count/10))

  pages = []

  for p in range(pagecount):

    pipeline = [
      {
      '$match': {
            
            'guild': ctx.guild.id,
            'readers.user': userid,
            
          }
      },
      {
        '$unwind': {
          'path': '$readers'
        }
      },
      {
        '$match': {
          'readers.user': userid
        }
      }, 
      {
        '$sort': {
          'readers.read': -1
        }
      },
      {
        '$skip': p * 10
      },
      {
        '$limit' : 10
      }

    ]
    found = books.aggregate(pipeline)

    embed = discord.Embed(title="Book listing", description= str(count) + " books in " + username + "'s hoard." )
    for b in found:
      embed.add_field(name=b['name'], value='Hoarded ' + str(b['readers']['read'].date()) , inline=False)
    
    pages.append(embed)
  
  if len(pages) == 0:
    await ctx.respond('Your hoard is lacking', ephemeral=ephem)
    return

  pagination = Paginator(pages=pages)
  await pagination.respond(ctx.interaction, ephemeral=ephem)

@bot.slash_command(name="leaderboard", description="See who's hoard is the biggest")
@guild_only()
async def leaderboard(ctx):
  countpipeline = [
      {'$match': {'guild': ctx.guild.id}},
      {'$unwind': {'path': '$readers'}}, 
      {'$replaceRoot': {'newRoot': '$readers'}}, 
      {
          '$group': {
              '_id': '$user', 
              'count': {
                  '$count': {}
              }
          }
      },
      {'$count': 'count'}
    ] 
  

  countagg = books.aggregate(countpipeline)

  crp = {}
  for l in countagg:
    crp = l

  pagecount = math.ceil((int(crp['count'])/10))

  pages = []
  place = 1
  count = int(crp['count'])

  for p in range(pagecount):
    pipeline = [
      {'$match': {'guild': ctx.guild.id}},
      {'$unwind': {'path': '$readers'}}, 
      {'$replaceRoot': {'newRoot': '$readers'}}, 
      {
          '$group': {
              '_id': '$user', 
              'count': {
                  '$count': {}
              }
          }
      },
      { '$sort': {'count': -1,},
      }, 
      { '$skip': p * 10 },
      { '$limit' : 10 }
    ] 

    found = books.aggregate(pipeline)

    embed = discord.Embed(title="Book listing", description= str(count) + " on the board.")
    for b in found:
      embed.add_field(name="", value=f"{place}: <@{str(b['_id'])}>\n**Books hoarded: {str(b['count'])}**", inline=False)
      place += 1
    
    pages.append(embed)
    
  
  if len(pages) == 0:
    await ctx.respond('Library Empty')
    return

  pagination = Paginator(pages=pages)
  await pagination.respond(ctx.interaction)

@bot.slash_command(name="start-session", description = "Starts a new reading session for your Flight")
@guild_only()
@default_permissions(manage_messages=True)
async def startSession(ctx):
  search = {
    'guild': ctx.guild.id,
    'ended': {'$exists': False}
  }

  # Caps so the server can only have one active session at a time.
  found = nominateSessions.count_documents(search, limit=1)
  if(found != 0):
    await ctx.respond('Your flight already have an active reading session.')
    return
  
  document = {
  'guild': ctx.guild.id,
  'added': datetime.now(),
  'user': ctx.author.id,
  'nominations': []
  }
  result = nominateSessions.insert_one(document)
  if (result.inserted_id): 
    await ctx.respond(f'<@{ctx.author.id}> started a new reading session.')
  else:
    await ctx.respond('Failed to start reading session')

@bot.slash_command(name="end-session", description = "Ends the current reading session for your Flight")
@guild_only()
@default_permissions(manage_messages=True)
async def endSession(ctx):
  search = {
    'guild': ctx.guild.id,
    'ended': {'$exists': False}
  }

  # Caps so the server can only have one active session at a time.
  found = nominateSessions.count_documents(search, limit=1)
  if(found == 0):
    await ctx.respond('Your flight doesn\'t have an active reading session.')
    return
    
  result = nominateSessions.update_one(search, {
    '$set': {
      'ended': datetime.now(),
      'endedUser': ctx.author.id
    }
  })

  if result.acknowledged:
    await ctx.respond('The current session has ended')
  else: 
    await ctx.respond('Failed to end the current session')

@bot.slash_command(name="nominate", description = "Nominate a book to your Flight's reading session")
@guild_only()
async def addNomination(ctx, book: str):
  book = pascal_case(str.strip(book))
  search = {
    'guild': ctx.guild.id,
    'ended': {'$exists': False}
  }

  # Caps so the server can only have one active session at a time.
  found = nominateSessions.count_documents(search, limit=1)
  if(found == 0):
    await ctx.respond('Your flight doesn\'t have an active reading session.')
    return
  
  existingNominationSearchPipeline = [
    {
        '$match': {
            'guild': ctx.guild.id, 
            'ended': {
                '$exists': False
            }
        }
    }, {
        '$unwind': '$nominations'
    }, {
        '$replaceRoot': {
            'newRoot': '$nominations'
        }
    }, {
        '$project': {
            'name': {
                '$toLower': '$name'
            }, 
            'user': True
        }
    }, {
        '$match': {
            'user': ctx.author.id
        }
    }, {
        '$match': {
            'name': book.lower()
        }
    }
  ]

  foundExistingNomination = nominateSessions.aggregate(existingNominationSearchPipeline)
  existingNominationCount = 0
  for d in foundExistingNomination:
    existingNominationCount += 1
  
  if existingNominationCount > 0:
    await ctx.respond(f'You already nominated {book}', ephemeral=True)
    return
  
  existingBookSearchPipeline = [
    {
        '$match': {
            'guild': ctx.guild.id
        }
    }, {
        '$project': {
            '_id': False, 
            'name': {
                '$toLower': '$name'
            }
        }
    }, {
        '$match': {
            'name': book.lower()
        }
    }
]

  foundExistingBooks = books.aggregate(existingBookSearchPipeline)
  existingBookCount = 0
  for d in foundExistingBooks:
    existingBookCount += 1
  
  if existingBookCount > 0:
    await ctx.respond(f'{book} cannot be nominated for it was already chosen by the club.', ephemeral=True)
    return
  
  foundSession = nominateSessions.find_one(search)
  search = {
    '_id': foundSession['_id'],
    'guild': ctx.guild.id,
  }
  
  readerobject = {
    'nominated': datetime.now(),
    'name': book,
    'user': ctx.author.id
  }
  result = nominateSessions.update_one(search, {
    '$push': {
      'nominations': readerobject
    }
  })

  if result.acknowledged:
    await ctx.respond(f'{book} nominated!')
  else: 
    await ctx.respond('Book could not be nominated')

@bot.slash_command(name="draw-nominees", description = "List all the book in your Flight's library")
@guild_only()
@default_permissions(manage_messages=True)
async def drawNominees(
  ctx, 
  min_nominations: Option(int, "Minimum of times the book received a nomination in the session search period.", min_value=2, default=2),
  past_sessions: Option(int, "How many prior sessions should be considered in the search.", min_value=0, default=0)):

  search = [
    {
        '$match': {
            'guild': ctx.guild.id
        }
    }, {
        '$sort': {
            'added': -1
        }
    }, {
        '$limit': past_sessions + 1
    }, {
        '$unwind': {
            'path': '$nominations'
        }
    }, {
        '$replaceRoot': {
            'newRoot': '$nominations'
        }
    }, {
        '$sortByCount': {
            '$toLower': '$name'
        }
    }, {
        '$match': {
            'count': {
                '$gt': min_nominations - 1
            }
        }
    }
  ]

  found = nominateSessions.aggregate(search)

  embed = discord.Embed(title="Book Nominees", description="Here are the chosen books with at least {} nominations".format(min_nominations))
  itemList = ""
  bookCount = 1
  for b in found:
    itemList += "\n{}. {} ({})".format(bookCount, pascal_case(b['_id']), b['count'])
    bookCount += 1

  embed.add_field(name="Nominees", value=itemList, inline=False)

  await ctx.respond(embed=embed, ephemeral=True)

@bot.slash_command(name="list-nominations", description="Lists all nomination for the current active session")
@guild_only()
async def listNominations(ctx, past_sessions: Option(int, "How many prior sessions should be considered in the search.", min_value=0, max_value=5, default=0)):

  search_count = [
    {
        '$match': {
            'guild': ctx.guild.id
        }
    }, {
        '$sort': {
            'added': -1
        }
    }, {
        '$limit': past_sessions + 1
    }, {
        '$unwind': {
            'path': '$nominations'
        }
    }, {
        '$replaceRoot': {
            'newRoot': '$nominations'
        }
    }, {
        '$sortByCount': {
            '$toLower': '$name'
        }
    }, {
        '$count': 'Total'
    }
  ]

  search = [
    {
        '$match': {
            'guild': ctx.guild.id
        }
    }, {
        '$sort': {
            'added': -1
        }
    }, {
        '$limit': past_sessions + 1
    }, {
        '$unwind': {
            'path': '$nominations'
        }
    }, {
        '$replaceRoot': {
            'newRoot': '$nominations'
        }
    }, {
        '$sortByCount': {
            '$toLower': '$name'
        }
    }, {
      '$sort': {
            '_id': 1
        }
    }
  ]

  found_count = nominateSessions.aggregate(search_count)
  count = 0
  for b in found_count:
    count = b['Total']

  found = nominateSessions.aggregate(search)

  pagecount = math.ceil((count/10))

  pages = []

  for p in range(pagecount):
    embed = discord.Embed(title="Book Nomination", description= str(count) + " books currently nominated" )
    itemList = ""
    bookCount = 1

    for b in found:
      itemList += "\n{}. {}".format(bookCount, pascal_case(str(b['_id'])))
      bookCount += 1
      
    embed.add_field(name='Current Nominated Books', value=itemList, inline=False)

    pages.append(embed)
  
  if len(pages) == 0:
    await ctx.respond('No books nominated yet', ephemeral=True)
    return

  pagination = Paginator(pages=pages)
  await pagination.respond(ctx.interaction, ephemeral=True)

async def getBook(book_url):
    book = await goodreads.getBook(book_url)
    if not book:
        return;
    
    embed = discord.Embed(
        title=book.full_title,
        url=book_url,
        description=book.description,
        color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
    )
    
    if book.series:
        embed.add_field(name="Series", value="[{}]({})".format(book.series, book.series_link), inline=False)    
    
    embed.add_field(name="Title", value="[{}]({})".format(book.title, book_url), inline=False)
    embed.add_field(name="Author(s)", value=formatAuthor(book.authors), inline=True)
    embed.add_field(name="Rating", value= ":star: " + book.rating, inline=True)
    # embed.add_field(name="Inline Field 3", value="Inline Field 3", inline=True)
 
    # embed.set_footer(text="The Awesome Lu Parser :3") # footers can have icons too
    embed.set_author(name="Goodreads / Library Card", icon_url="https://www.goodreads.com/favicon.ico")
    # embed.set_thumbnail(url="https://example.com/link-to-my-thumbnail.png")
    embed.set_image(url=book.image_link)

    return embed # Send the embed with some text

def pascal_case(input_str):
    words = input_str.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)

def formatAuthor(authors):
    formattedAutors = []
    for author in authors:
        formattedAutors.append("[{}]({})".format(author.name, author.link))    
    return ", ".join(formattedAutors)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="dragons!"))

@bot.event
async def on_message(message: discord.message):
    # so the bot wont respond itself
    if message.author == bot.user:
        return

    if message.content.startswith(("https://www.goodreads.com/book/show/", "https://goodreads.com/book/show/")) :
        
        book_url = message.content.split()[0]

        embed = await getBook(book_url)

        
        if embed:
            await message.channel.send(embed=embed, reference=message.to_reference())
            await message.edit(suppress = True)

bot.run(os.getenv('TOKEN'))