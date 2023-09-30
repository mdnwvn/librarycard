import discord
import os
from dotenv import load_dotenv
import typing
import pymongo
from bson.objectid import ObjectId
import math
from discord.ext.pages import Paginator, Page
from pymongo import TEXT
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
from discord import default_permissions
from discord import guild_only


load_dotenv()

client = pymongo.MongoClient(os.getenv('MONGO_STRING'))
books = client.librarycard.books

books.create_index([('name', TEXT)])
books.create_index([('guild', ASCENDING)])
books.create_index([('readers.user', ASCENDING)])

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot()

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
    },{
        '$sort': {
          'added': -1
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

    embed = discord.Embed(title="Book listing", description= str(count) + " books left.")
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

bot.run(os.getenv('TOKEN'))