import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from config import token, ping_role_id
import valo_info
import asyncio, random, re
from datetime import datetime, timedelta


bot = commands.Bot(
    command_prefix = commands.when_mentioned,
    intents = discord.Intents.all()
)

# Global Variables
users = ""
user_list = []
counter = 1
check = False


@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    await bot.tree.sync()


@bot.tree.command(name="info", description="Shows info about any Valorant Account")
@app_commands.describe(name="Enter your Valorant Name")
@app_commands.describe(tag="Enter your Valorant Tag")
async def info(i:discord.Interaction, name:str, tag:str):
    embed = discord.Embed(
        color=discord.Color.red(),
        title=f"{name}'s info"
    )

    await i.response.defer()
    
    account_info = await valo_info.acc_info(name,tag)
    
    if account_info['status'] == 404:
        embed.description = "## ERROR 404\n***Account not found. Please enter correct details***"
        await i.followup.send(embed=embed)
        
    elif account_info['status'] == 200:
        mmr_info = await valo_info.mmr_info_v1(puuid=account_info['data']['puuid'])
        match_info = await valo_info.mmr_info_v2(puuid=account_info['data']['puuid'])

        embed.add_field(name="Valorant Tag:", value=f"```{mmr_info['data']['name']}#{mmr_info['data']['tag']}```", inline=False)
        embed.add_field(name="Level:", value=f"{account_info['data']['account_level']}", inline=True)
        embed.add_field(name="Current Rank:", value=f"{mmr_info['data']['currenttierpatched']}", inline=True)
        embed.add_field(name="Highest Rank:", value=f"{match_info['data']['highest_rank']['patched_tier']}", inline=True)

        embed.set_thumbnail(url=f"{mmr_info['data']['images']['large']}")
        embed.set_image(url=f"{account_info['data']['card']['wide']}")

        print("Entering for loop")
        by_season = list(match_info['data']['by_season'])
        print("match_info by season", by_season)
        for x in range(1, 4):
            print("Enters for loop")
            if "error" in  match_info['data']['by_season'][by_season[-x]]:
                print(match_info['data']['by_season'][by_season[-x]])
                print("Has error in match_info. Field Added")
                embed.add_field(
                    name=f"{(str(by_season[-x])).replace('e', 'Episode ').replace('a', ' Act ')}",
                    value="No Games Played",
                    inline=False
                    )
            else:
                print("Enters else block")
                print((str(by_season[-x])).replace('e', 'Episode ').replace('a', ' Act '))

                final_rank = match_info['data']['by_season'][by_season[-x]]['final_rank_patched']
                total_matches = match_info['data']['by_season'][by_season[-x]]['number_of_games']
                wins = match_info['data']['by_season'][by_season[-x]]['wins']
                win_rate = round((wins/total_matches)*100,1)
                
                embed.add_field(
                    name=f"{(str(by_season[-x])).replace('e', 'Episode ').replace('a', ' Act ')}", 
                    value=f"Rank Achieved: **{final_rank}**\nTotal matches: **{total_matches}**\nWins: **{wins}**\nWin Rate: **{win_rate}%**", 
                    inline=False
                    )
        
        await i.followup.send(embed=embed)

    


@bot.tree.command(name="store", description="Shows what's on the featured store")
async def store(i:discord.Interaction):
    store = await valo_info.featured_store()

    await i.response.defer()

    if store['status'] == 200:
        embed = discord.Embed(
            title="Featured Store",
            description=f"**Bundle Price: {store['data'][0]['bundle_price']}**",
            color=discord.Color.from_str("#ff0000")
        )
        embed.add_field(
            name=f"{store['data'][0]['items'][0]['name']}", 
            value=f"Price: {store['data'][0]['items'][0]['base_price']}"
            )
        embed.set_image(url=f"{store['data'][0]['items'][0]['image']}")

        for item in store['data'][0]['items']:
            if item['type'] == 'player_card':
                embed.set_thumbnail(url=f"{item['image']}")
                break
        

        
        previous_button = Button(label="Previous", style=discord.ButtonStyle.red)
        next_button = Button(label="Next", style=discord.ButtonStyle.red)

        async def next_callback(ni:discord.Interaction):
            global counter
            embed.clear_fields()
            previous_button.disabled = False
            counter = counter + 1
            embed.add_field(name=f"{store['data'][0]['items'][counter]['name']}", value=f"Price: {store['data'][0]['items'][counter]['base_price']}")
            embed.set_image(url=f"{store['data'][0]['items'][counter]['image']}")

            await ni.response.defer()

            if counter == (len(store['data'][0]['items'])-1):
                next_button.disabled=True
                await i.edit_original_response(embed=embed, view= views)
            else:
                await i.edit_original_response(embed=embed, view= views)

        async def previous_callback(pi:discord.Interaction):
            global counter
            embed.clear_fields()
            next_button.disabled = False
            counter = counter - 1
            embed.add_field(name=f"{store['data'][0]['items'][counter]['name']}", value=f"Price: {store['data'][0]['items'][counter]['base_price']}")
            embed.set_image(url=f"{store['data'][0]['items'][counter]['image']}")

            await pi.response.defer()

            if counter ==0:
                previous_button.disabled=True
                await i.edit_original_response(embed=embed, view=views)
            else:
                await i.edit_original_response(embed=embed, view= views)


        previous_button.callback = previous_callback
        next_button.callback = next_callback

        views = View()
        views.add_item(previous_button)
        views.add_item(next_button)
        previous_button.disabled = True

        await i.edit_original_response(embed=embed, view=views)

    else:
        await i.edit_original_response("`Status code!=200`\nError... Try again later or change input")



@bot.tree.command(name="queue", description="Start a timer that pings everyone and asks them to join")
@app_commands.describe(time="Enter time in minutes")
async def queue(i:discord.Interaction, time:int=10):
    global counter, users, check, user_list

    user_list = [i.user.id]

    remind_time = datetime.now() + timedelta(minutes=time)
    timestamp = int(remind_time.timestamp())
    embed = discord.Embed(
        title="Wanna Play Valo??",
        description=f"**Time left to join <t:{timestamp}:R>\n**{i.user.mention} is calling everyone to play\n**Click on the Button below to join**",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=i.user.avatar.url)

    embed2 = discord.Embed(
        title="Let's Play Valo!",
        color=discord.Color.red()
    )
    users = f"{i.user.mention}"

    join_button = Button(label="Join", style=discord.ButtonStyle.blurple)
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def join_callback(jint:discord.Interaction):
        global user_list, users, counter

        if jint.user.id not in user_list:
            user_list.append(jint.user.id)
            
            await jint.response.defer()
            users = users + f"{jint.user.mention}"
            embed.add_field(name=f"Player {counter}", value=f"{jint.user.mention} is joining", inline=False)
            counter = counter + 1
            await i.edit_original_response(embed=embed, view=views)
        else:
            await jint.response.send_message(content="You have already joined", ephemeral=True)

    async def cancel_callback(cint:discord.Interaction):
        global check, counter
        await cint.response.defer()
        if cint.user == i.user:
            check = True
            counter = 1
            embed.description = "Queue Cancelled"
            embed.clear_fields()
            await i.edit_original_response(content="", embed=embed, view=None)
        else:
            await cint.followup.send(content="Only Command User can Cancel", ephemeral=True)
    
    join_button.callback = join_callback
    cancel_button.callback = cancel_callback

    views = View()
    views.add_item(join_button)
    views.add_item(cancel_button)

    embed.add_field(name=f"Player {counter}",value=f"{i.user.mention} is joining", inline=False)
    counter = counter + 1
    ping_role = i.guild.get_role(ping_role_id)
    await i.response.send_message(content=f"{ping_role.mention}",embed=embed, view=views, allowed_mentions=discord.AllowedMentions(roles=True))

    gifs =[
        "https://media.giphy.com/media/jRtZJvoWxWVJ7uF1cx/giphy.gif",
        "https://media.giphy.com/media/woX7AfeiJ4pwSWJ8xY/giphy.gif",
        "https://media.giphy.com/media/IvOFcGZeDA76P6XryO/giphy.gif",
        "https://media.giphy.com/media/jRtZJvoWxWVJ7uF1cx/giphy.gif",
        "https://media.giphy.com/media/sUOkBnwf8157cVGE57/giphy.gif"
        ]
    
    await asyncio.sleep(time*60)
    print(check)
    if check == False:
        counter = 1
        embed2.set_image(url=random.choice(gifs))
        await i.edit_original_response(embed=embed, view=None)
        await i.followup.send(content=f"{users}",embed=embed2)

#-----------------
bot.run(token)
#-----------------
