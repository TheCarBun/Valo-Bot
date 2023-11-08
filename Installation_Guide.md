<h1 align="center">
  <br>
  <img width=100% src="https://imgur.com/dOp3qNM.png" alt="Valo Bot Banner">
</h1>

<h4 align="center"> A Valorant Discord bot that shows player info and stats.</h4>
<hr>

<h1 align="center">
Installation Guide </h1>

> **Warning**
>
> #### ***Do not make this bot public. Henrik-3's API is for educational purposes only!***

>[!Important]
>
> Explore all API details [here](https://github.com/Henrik-3/unofficial-valorant-api), including what you're allowed to do and what's off-limits. By recreating this bot, you confirm that you've thoroughly read all warnings.


## Step 1:

#### Fork this repository.
* If you don't yet have a Github account, [create one](https://github.com/join)! It's free and easy.
* Click [here](https://github.com/TheCarBun/valo-bot/fork) or use the button in the upper righthand side of this page to fork the repository so that it will be associated with your Github account.


* Please **star our project** if you like it using the top-right Star icon. Every star helps us! 


## Step 2:

#### Create a new [Discord Application](https://discordapp.com/developers/applications) in the Discord Developer Portal
* Give app a friendly name and click the **Create App** button
* Scroll down to the **Bot** section
* Click the **Create a Bot User** button
* Click the **Yes, do it!** button
* Reset and copy the bot's **TOKEN**, you will need it later
* Under **Privileged Gateway Intents** enable **MESSAGE CONTENT INTENT**

## Step 3:

Invite your bot to your discord server:

* Go to OAuth2 section then Url Generator
* Under Scopes enable:
  * `x` `bot`
  * `x` `application.commands`
* Under Bot Permission enable:
  * `x` `Manage Webhooks`
  * `x` `Read Messages/View Channels`
  * `x` `Send Messages`
  * `x` `Embed Links`
  * `x` `Attach Files`
  * `x` `Read Message History`
  * `x` `Mention Everyone`
  * `x` `Use Slash Commands`

* Invite your bot to the server with the generated URL

## Step 4:

Install all requirements from [requirements.txt](requirements.txt) with
```
pip install -r requirements.txt
```
Or
<br>
Manually install the following packages:
```
pip discord.py
```

## Step 5:

```
token = "TOKEN"
ping_role_id = "ROLE ID"
```

* Replace `TOKEN` with your bot token in [config.py](config.py) file.
* If you want to use `/queue` command:
  * Replace `ROLE_ID` in the config file with the role ID of the role that you want to ping while starting queue.
  * If you want to use `@everyone` instead of a ping role:
    * Replace this line 
    ```
    ping_role = i.guild.get_role(ping_role_id)
    await i.response.send_message(content=f"{ping_role.mention}",embed=embed, view=views, allowed_mentions=discord.AllowedMentions(roles=True))
    ```
  
    * with this
    ```
    await i.response.send_message(content="@everyone",embed=embed, view=views, allowed_mentions=discord.AllowedMentions(roles=True))
    ```

## Step 6:

Run the bot

