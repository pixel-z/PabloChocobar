import requests
import webbrowser
import subprocess

# Set parameters
handle = "tourist"
min_rating = 1600
max_rating = 1700

# Returns list of contest IDs from which problems are to be picked
def fetch_contests():
    data = requests.get("https://codeforces.com/api/contest.list").json()
    contests = []
    for i in data['result']:
        if "ducational" in i['name']:
            contests.append(i['id'])
        if "ICPC" in i['name'] and "otlin" not in i['name']:
            contests.append(i['id'])
    return contests

# Returns desirable problems in sorted order
def fetch_total_problems(contests):
    data = requests.get(
        "https://codeforces.com/api/problemset.problems").json()
    total_problems = []
    for i in data['result']['problems']:
        if i['contestId'] in contests:
            try:
                if i['rating'] >= min_rating and i['rating'] <= max_rating:
                    total_problems.append(i)
            except:
                pass
    total_problems.reverse()
    total_problems.sort(key=lambda x: x["rating"])
    return total_problems

# Return problems already solved by the user
def fetch_user_solves():
    problems_finished = []
    data = requests.get(
        "https://codeforces.com/api/user.status?handle="+handle).json()
    try:
        for i in data['result']:
            if i['verdict'] == "OK":
                problems_finished.append(i['problem'])
    except:
        pass
    return problems_finished

# Search and print the most relevant problem
def search(total_problems, problems_finished):
    found_status = False
    todo = None
    done = 0
    for i in total_problems:
        if i in problems_finished:
            done += 1
        elif found_status is False:
            todo = i
            found_status = True
    if found_status==True:
        url = 'https://codeforces.com/contest/' + \
            str(todo['contestId'])+'/problem/'+todo['index']
        # print("\nSuggested Problem: "+todo['name'])
        # print("Link: "+url)
        # print("Current Progress: "+str(done)+'/' +
        #     str(len(total_problems))+' Problems\n')
        name = "\nSuggested Problem: "+todo['name']
        link = "Link: "+url
        progress = "Current Progress: "+str(done)+'/' + str(len(total_problems))+' Problems\n'
        return name, link, progress
    else:
        print("\nAll problems from this range have been completed!\n")
        return None, None, None # condition when all problems done in the range

def get_problems(h, min, max):
    global handle, min_rating, max_rating
    handle = h
    min_rating = int(min)
    max_rating = int(max)
    
    # Calling relevent functions
    _contests = fetch_contests()
    _total_problems = fetch_total_problems(_contests)
    _problems_finished = fetch_user_solves()
    name, link, progress = search(_total_problems, _problems_finished)
    return name, link, progress

# Discord.py code
async def process_msg(message):
    msg = message.split()
    print(msg)

    if (len(msg) != 3 and len(msg) != 4):
        print("Usage: -gimme <handle> <min_rating> <max_rating>")
        reply = "```Usage: -gimme <handle> <min_rating> <max_rating>```"
        return reply, reply, reply  # error criteria
    else:
        handle = msg[1]
        min_rating = msg[2]
        max_rating = msg[2]
        if (len(msg) == 4):
            max_rating = msg[3]
        print("handle: " + handle)
        print("min_rating: " + min_rating)
        print("max_rating: " + max_rating)

        # obj = subprocess.Popen('python3 z.py ' + handle + ' ' + min_rating + ' ' + max_rating, shell=True)
        name, link, progress = get_problems(handle, min_rating, max_rating)
        return name, link, progress

import discord
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('-help'):
        ret = "```-help: Get this message\n-gimme: Get a problem```"
        await message.channel.send(ret)

    if message.content.startswith('-gimme'):
        name, link, progress = await process_msg(message.content)
        # await message.channel.send('I read ' + message.content)
        
        if name == None and link == None and progress == None:
            await message.channel.send("```All the problems in the specified range completed.```")
        # Error condition
        elif name == link and link == progress:
            await message.channel.send("```Usage: -gimme <handle> <rating>\nUsage: -gimme <handle> <min_rating> <max_rating>```")
        else:
            ret = name+'\n'+progress+link
            await message.channel.send(ret)

import os
# from dotenv import load_dotenv
# load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client.run(TOKEN)