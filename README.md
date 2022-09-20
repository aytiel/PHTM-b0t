# GW2 Log Bot
### For all of your raid and fractal log needs!
<img align="right" src="https://vignette.wikia.nocookie.net/gwwikia/images/4/4d/Guild_Wars_2_Dragon_logo.jpg/revision/latest?cb=20090825055046" height="128" width="128"></img>

The intention of this Discord bot is to automate the monotonous process of manually uploading and posting logs after every raid or fractal clear. At the call of a single command, your most recent logs will be uploaded to both [dps.report](https://dps.report/) and ~GW2Raidar~<b>(deprecated)</b>, and all of the links will be posted in your Discord server within minutes.

<b>Supported languages:</b> English, German, French, Spanish

## This project has been discontinued. Thank you for all of the support over the years!
## Installing the bot
<b>1.</b> Install Python 3.6+. To guarantee the best results, install Python 3.6.5([32-bit](https://www.python.org/ftp/python/3.6.5/python-3.6.5.exe))([64-bit](https://www.python.org/ftp/python/3.6.5/python-3.6.5-amd64.exe)). <br />
<b>2.</b> During the setup, make sure to tick `Install launcher for all users (recommended)` and `Add Python 3.6 to PATH`. <br />
<b>3.</b> Install [Git for Windows](https://git-scm.com/downloads). <br />
<b>4.</b> During the setup, make sure to tick `Use Git from the Windows Command Prompt`, <br /> `Checkout Windows-style, commit Unix-style endings`, and `Use MinTTY (the default terminal MSYS2)`. <br />
<b>5.</b> Open Git Bash by right-clicking inside the empty space of the folder where you would like to <br /> keep the bot and clicking `Git Bash Here`. <br />
<b>6.</b> In the command window that opens, run the following command: <br />`git clone https://github.com/aytiel/PHTM-b0t.git GW2LogBot -b gw2-uploader`. <br />

## Setting up the bot
<b>Note:</b> You can skip steps 1 and 2 if somebody is already running an instance of the GW2 Log Bot in your Discord server. <br />
<b>1.</b> Create a bot account. Helpful tutorials can be found [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token) and [here](https://twentysix26.github.io/Red-Docs/red_guide_bot_accounts/). <br />
<b>2.</b> Invite the bot to your Discord server using the following link: <br />`https://discordapp.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=27648&scope=bot`. <br /> Make sure you replace `YOUR_CLIENT_ID` with the client id listed on your application page. <br />
<b>3.</b> Update `settings/config.py` with the token associated with your bot account. <br />`TOKEN = 'BOT_TOKEN_HERE'` <br /> You can open the `settings/config.py` file using Notepad or [Notepad++](https://notepad-plus-plus.org/download/). <br /> Also, feel free to change the command `PREFIX` as well if you wish. <br />
<b>4.</b> Double-click on `install.sh` to install all the required dependencies. <br />
<b>5.</b> Run the bot by double-clicking the `run_bot.sh` script. The script should update the bot to the latest version and then run it. If the update fails, you can retrieve a fresh, up-to-date copy by repeating Steps **5** and **6** of **Installing the bot**. <br />

**Join the [Discord](https://discord.gg/PFcM9cJ) server for questions, concerns, and troubleshooting and for access to custom boss icons for more aesthetic log posting.**

## Commands
The default prefix is `$`.

<div style="overflow-x:auto;">
  <table width=180 style='table-layout:fixed'>
    <col width=20>
 	    <col width=100>
    <thead>
      <tr>
        <th>Command</th>
        <th>Description</th>
      </tr>
    </thead>
    <tr>
      <td><b>login</b></td>
      <td>Assigns the bot to you.</td>
    </tr>
    <tr>
    </tr>
    <tr>
      <td><b>upload [raids/fractals]<br />(title)<br />(--time)<br />(--num x)</b></td>
      <td>Uploads raid or fractal logs.<br />(Optional) Add a title to the post<br />(Optional) Include the killtime for each boss in the log post<br />(Optional) Upload the x most recent logs of each selected boss</td>
    </tr>
    <tr>
      <td><b>shutdown</b></td>
      <td>Shuts down the bot. Recommended for when you are finished using the bot.</td>
    </tr>
  </table>
</div>

### Preview
<img align="middle" src="https://github.com/aytiel/PHTM-b0t/blob/gw2-uploader/images/previewv2.PNG" height="325" width="395"></img>
<img align="middle" src="https://github.com/aytiel/PHTM-b0t/blob/gw2-uploader/images/previewv2_1.PNG" height="191" width="400"></img>

## Caveats
<ul>
  <li>Only the person booting up the bot may upload logs. You should be able to tell who the current user of the bot is by looking at the bot's activity status. It should say <b>Current User: SOME_USER</b>.
  <li>Due to no official updates from the new GW2Raidar team, uploading to GW2Raidar has been <b>deprecated</b> until further notice.
</ul>
