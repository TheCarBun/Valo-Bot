import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from config import *
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
        color=discord.Color.from_str("#FD4556"),
        title=f"{name}'s info"
    )
    
    await i.response.defer()

    account_info = await valo_info.acc_info(name, tag)

    if account_info['status'] == 404:
        embed.description = "## ERROR 404\n***Account not found. Please enter correct details***"
        await i.followup.send(embed=embed)

    elif account_info['status'] == 200:
        mmr_info = await valo_info.mmr_info_v1(puuid=account_info['data']['puuid'])
        match_info = await valo_info.mmr_info_v2(puuid=account_info['data']['puuid'])

        embed.add_field(name="Valorant Tag:",
            value=f"```{account_info['data']['name']}#{account_info['data']['tag']}```",
            inline=False)
        embed.add_field(name="Level:",
                        value=f"{account_info['data']['account_level']}",
                        inline=True)
        embed.add_field(name="Current Rank:",
                        value=f"{mmr_info['data']['currenttierpatched']}",
                        inline=True)
        embed.add_field(
            name="Highest Rank:",
            value=f"{match_info['data']['highest_rank']['patched_tier']}",
            inline=True)
        embed.set_image(url=f"{account_info['data']['card']['wide']}")

        #If Unranked and has no image
        if mmr_info['data']['images'] != None:
            embed.set_thumbnail(url=f"{mmr_info['data']['images']['large']}")
        else:
            embed.set_thumbnail(url=f"{account_info['data']['card']['small']}")

        by_season = list(match_info['data']['by_season'])
        for x in range(1, 4):
            if "error" in match_info['data']['by_season'][by_season[-x]]:
                embed.add_field(name=f"{(str(by_season[-x])).replace('e', 'Episode ').replace('a', ' Act ')}",
                    value="No Games Played",
                    inline=False)
            else:

                final_rank = match_info['data']['by_season'][by_season[-x]]['final_rank_patched']
                total_matches = match_info['data']['by_season'][by_season[-x]]['number_of_games']
                wins = match_info['data']['by_season'][by_season[-x]]['wins']
                win_rate = round((wins / total_matches) * 100, 1)

                embed.add_field(name=f"{(str(by_season[-x])).replace('e', 'Episode ').replace('a', ' Act ')}",
                    value=f"Rank Achieved: **{final_rank}**\nTotal matches: **{total_matches}**\nWins: **{wins}**\nWin Rate: **{win_rate}%**",
                    inline=False)

        await i.followup.send(embed=embed)

    


@bot.tree.command(name="store", description="Shows what's on the featured store")
async def store(i:discord.Interaction):
    store = await valo_info.featured_store()

    await i.response.defer()

    if store['status'] == 200:
        expires_at = datetime.now() + timedelta(seconds=store['data'][0]['seconds_remaining'])
        timestamp = int(expires_at.timestamp())
        embed = discord.Embed(
            title="Featured Store",
            description=f"**Bundle Price: `{store['data'][0]['bundle_price']} VP`**\n**Expires At:** <t:{timestamp}:f>",
            color=discord.Color.from_str("#FD4556")
        )
        embed.add_field(
            name=f"{store['data'][0]['items'][0]['name']}", 
            value=f"Price: `{store['data'][0]['items'][0]['base_price']} VP`"
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
            embed.add_field(name=f"{store['data'][0]['items'][counter]['name']}", value=f"Price: `{store['data'][0]['items'][counter]['base_price']} VP`")
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
            embed.add_field(name=f"{store['data'][0]['items'][counter]['name']}", value=f"Price: `{store['data'][0]['items'][counter]['base_price']} VP`")
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


# WIP Need to make this better

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
        color=discord.Color.from_str("#FD4556")
    )
    embed.set_thumbnail(url=i.user.avatar.url)

    embed2 = discord.Embed(
        title="Let's Play Valo!",
        color=discord.Color.from_str("#FD4556")
    )
    users = f"{i.user.mention}"

    join_button = Button(label="Join", style=discord.ButtonStyle.blurple)
    unjoin_button = Button(label="Unjoin", style=discord.ButtonStyle.gray)
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)
    end_button = Button(label="End Queue", style=discord.ButtonStyle.red)

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

    async def unjoin_callback(ujint:discord.Interaction):
        await ujint.response.defer()
        global user_list, users, counter

        if ujint.user.id in user_list:
            user_list.remove(ujint.user.id)
            users = users.replace(f"{ujint.user.mention}", "")
            embed.add_field(name="Player Unjoined", value=f"{ujint.user.mention}", inline=False)
            counter = counter - 1
            await i.edit_original_response(embed=embed, view=views)
        else:
            await ujint.followup.send(content="You have not joined yet", ephemeral=True)
            

    async def cancel_callback(cint:discord.Interaction):
        global check, counter
        await cint.response.defer()
        if cint.user == i.user:
            check = True #checks if queue was cancelled
            counter = 1 #resets counter to 1
            embed.description = "Queue Cancelled"
            embed.clear_fields()
            await i.edit_original_response(content="", embed=embed, view=None)
        else:
            await cint.followup.send(content="Only Command User can Cancel", ephemeral=True)
    
    async def end_callback(eint:discord.Interaction):
        global check, counter
        if eint.user == i.user:
            check = True
            counter = 1
            embed2.set_image(url=random.choice(gifs))
            await i.edit_original_response(embed=embed, view=None)
            await i.followup.send(content=f"{users}",embed=embed2)

    
    join_button.callback = join_callback
    unjoin_button.callback = unjoin_callback
    cancel_button.callback = cancel_callback
    end_button.callback = end_callback

    views = View(timeout=time*60)
    views.add_item(join_button)
    views.add_item(unjoin_button)
    views.add_item(cancel_button)
    views.add_item(end_button)

    embed.add_field(name=f"Player {counter}",value=f"{i.user.mention} is joining", inline=False)
    counter = counter + 1
    ping_role = i.guild.get_role(ping_role_id)
    await i.response.send_message(content=f"{ping_role.mention}",embed=embed, view=views, allowed_mentions=discord.AllowedMentions(roles=True))
    
    await asyncio.sleep(time*60)
    if check == False:
        counter = 1
        embed2.set_image(url=random.choice(gifs))
        await i.edit_original_response(embed=embed, view=None)
        await i.followup.send(content=f"{users}",embed=embed2)

# WIP Need to think of how to use this peroperly

@bot.tree.command(name="news", description="Shows recent Valorant related updates")
async def news(i:discord.Interaction):
    await i.response.defer()
    global counter
    counter = 1
    news = await valo_info.news()


    if news['status'] == 200:
        date = datetime.fromisoformat(news['data'][0]['date'])
        timestamp = int(date.timestamp())
        title = str(news['data'][0]['category']).capitalize()

        data = news['data'][0]

        embed = discord.Embed(
            title= title,
            url= news['data'][0]['external_link'],
            description=f"[{data['title']}]({data['url']})\n\nPosted <t:{timestamp}:R>",
            color=discord.Color.from_str("#FD4556")
        )
        embed.set_image(url=f"{data['banner_url']}")

        

        
        previous_button = Button(label="Previous", style=discord.ButtonStyle.red)
        next_button = Button(label="Next", style=discord.ButtonStyle.red)

        async def next_callback(ni:discord.Interaction):
            global counter
            previous_button.disabled = False
            counter = counter + 1

            date = datetime.fromisoformat(news['data'][counter]['date'])
            timestamp = int(date.timestamp())

            embed.clear_fields()
            embed.url = news['data'][counter]['external_link']
            embed.description = f"[{news['data'][counter]['title']}]({news['data'][counter]['url']})\n\nPosted <t:{timestamp}:R>\n\n"
            embed.set_image(url=f"{news['data'][counter]['banner_url']}")

            await ni.response.defer()

            if counter == (len(news['data'])-1):
                next_button.disabled=True
                await i.edit_original_response(embed=embed, view= views)
            else:
                await i.edit_original_response(embed=embed, view= views)

        async def previous_callback(pi:discord.Interaction):
            global counter
            next_button.disabled = False
            counter = counter - 1

            embed.clear_fields()
            date = datetime.fromisoformat(news['data'][counter]['date'])
            timestamp = int(date.timestamp())
            embed.url = news['data'][counter]['external_link']
            embed.description = f"[{news['data'][counter]['title']}]({news['data'][counter]['url']})\n\nPosted <t:{timestamp}:R>\n\n"
            embed.set_image(url=f"{news['data'][counter]['banner_url']}")

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

@bot.tree.command(name="crosshair", description="Get image of crosshair from ID")
async def crosshair(i:discord.Interaction, id:str):
    await i.response.defer()
    embed = discord.Embed(
        title="Crosshair Details",
        description=f"Crosshair ID: \n```{id}```",
        color=discord.Color.from_str("#FD4556")
    )
    embed.set_thumbnail(url=i.user.avatar.url)

    crosshair = await valo_info.fetch_crosshair(id=id)

    embed.set_image(url=crosshair)
    await i.edit_original_response(embed=embed)

#-----------------
bot.run(token)
#-----------------
