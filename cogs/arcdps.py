import json
import requests
import datetime
import time
import glob
import os

import discord
from discord.ext import commands
import settings.config

logs = {
    'raids': {
        'W1': {
            'Vale Guardian': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 15438, 'link': 'about:blank', 'success': False}},
            'Gorseval the Multifarious': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 15429, 'link': 'about:blank', 'success': False}},
            'Sabetha the Saboteur': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 15375, 'link': 'about:blank', 'success': False}}
        },
        'W2': {
            'Slothasor': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 16123, 'link': 'about:blank', 'success': False}},
            'Matthias Gabrel': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 16115, 'link': 'about:blank', 'success': False}}
        },
        'W3': {
            'Keep Construct': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 16235, 'link': 'about:blank', 'success': False}},
            'Xera': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 16246, 'link': 'about:blank', 'success': False}}
        },
        'W4': {
            'Cairn the Indomitable': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17194, 'link': 'about:blank', 'success': False}},
            'Mursaat Overseer': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17172, 'link': 'about:blank', 'success': False}},
            'Samarog': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17188, 'link': 'about:blank', 'success': False}},
            'Deimos': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17154, 'link': 'about:blank', 'success': False}}
        },
        'W5': {
            'Soulless Horror': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 19767, 'link': 'about:blank', 'success': False}},
            'Dhuum': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 19450, 'link': 'about:blank', 'success': False}}
        }
    },
    'fractals': {
        '99CM': {
            'MAMA': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17021, 'link': 'about:blank', 'success': False}},
            'Nightmare Oratuss': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17028, 'link': 'about:blank', 'success': False}},
            'Ensolyss of the Endless Torment': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 16948, 'link': 'about:blank', 'success': False}}
        },
        '100CM': {
            'Skorvald the Shattered': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17632, 'link': 'about:blank', 'success': False}},
            'Artsariiv': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17949, 'link': 'about:blank', 'success': False}},
            'Arkk': {'dps.report': 'about:blank', 'GW2Raidar': {'id': 17759, 'link': 'about:blank', 'success': False}}
        }
    }
}

logs_order = {
    'raids': {
        'W1': ['Gorseval the Multifarious', 'Sabetha the Saboteur', 'Vale Guardian'],
        'W5': ['Soulless Horror', 'Dhuum'],
        'W2': ['Slothasor', 'Matthias Gabrel'],
        'W4': ['Cairn the Indomitable', 'Mursaat Overseer', 'Samarog', 'Deimos'],
        'W3': ['Keep Construct', 'Xera']
    },
    'fractals': {
        '100CM': ['Skorvald the Shattered', 'Artsariiv', 'Arkk'],
        '99CM': ['MAMA', 'Nightmare Oratuss', 'Ensolyss of the Endless Torment']
    }
}

class Arcdps:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def upload(self, ctx, type: str, name: str):
        guild = ctx.guild
        if guild is None:
            has_perms = False
        else:
            has_perms = ctx.channel.permissions_for(guild.me).manage_messages
        if has_perms:
            await ctx.message.delete()
        else:
            await ctx.send('I do not have permissions to delete messages. Please enable this in the future.')
            
        if not type == 'raids' and not type == 'fractals':
            return await ctx.send('Please indicate whether you want to upload **raids** or **fractals** logs.')
        
        logs_length = 0
        for e in logs_order[type]:
            for b in logs_order[type][e]:
                logs_length += 1
                path = 'C:/Users/atl/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/' + b + '/*'
                all_files = glob.glob(path)
                latest_file = max(all_files, key=os.path.getctime)
                if latest_file is None:
                    error = 'ERROR :robot: : an error has occurred with ' + b + '. `Error Code: BLOODSTONE`.'
                    await ctx.send(error)
                    continue
                        
                dps_endpoint = 'https://dps.report/uploadContent?json=1&generator=ei'
                with open(latest_file, 'rb') as file:
                    files = {'file': file}
                    res = requests.post(dps_endpoint, files=files)
                    if not res.status_code == 200:
                        error = 'ERROR :robot: : an error has occurred with ' + b + '. `Error Code: DHUUMFIRE`.'
                        await ctx.send(error)
                        continue
                    else:
                        logs[type][e][b]['dps.report'] = res.json()['permalink']
                print('Uploaded ' + b + ': dps.report')
                    
                raidar_endpoint = 'https://www.gw2raidar.com/api/v2/token'
                cred = {'username': settings.config.RAIDARUSER, 'password': settings.config.RAIDARPASS}
                res = requests.post(raidar_endpoint, data=cred)
                if not res.status_code == 200:
                    error = 'ERROR :robot: : an error has occurred with ' + b + '. `Error Code: RYTLOCK`.'
                    await ctx.send(error)
                    continue
                else:
                    token = res.json()['token']
                    auth = 'Token ' + token
                    raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters/new'
                    with open(latest_file, 'rb') as file:
                        files = {'file': file}
                        res = requests.put(raidar_endpoint, headers={'Authorization': auth}, files=files)
                        if not res.status_code == 200:
                            error = 'ERROR :robot: : an error has occurred with ' + b + '. `Error Code: ZOJJA`.'
                            await ctx.send(error)
                            continue
                        else:
                            logs[type][e][b]['GW2Raidar']['success'] = True
                print('Uploaded ' + b + ': GW2Raidar')          
        
        counter = 0
        await self.update_raidar(ctx, type, counter, logs_length)
        await self.print_logs(ctx, type, name)
        
    async def update_raidar(self, ctx, type: str, counter: int, length: int):
        if length == 0:
            return
            
        pos = length - 1    
        for e in logs_order[type]:
            for b in logs_order[type][e]:
                if logs[type][e][b]['GW2Raidar']['success'] == False:
                    continue
                raidar_endpoint = 'https://www.gw2raidar.com/api/v2/token'
                cred = {'username': settings.config.RAIDARUSER, 'password': settings.config.RAIDARPASS}
                res = requests.post(raidar_endpoint, data=cred)
                if not res.status_code == 200:
                    error = 'ERROR :robot: : an error has occurred. `Error Code: RYTLOCK`.'
                    await ctx.send(error)
                    continue
                else:
                    token = res.json()['token']
                    auth = 'Token ' + token
                    raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters?limit=' + str(length)
                    res = requests.get(raidar_endpoint, headers={'Authorization': auth})
                    if not res.status_code == 200:
                        error = 'ERROR :robot: : an error has occurred. `Error Code: EIR`.'
                        return await ctx.send(error)
                    else:
                        if res.json()['results'][pos]['area_id'] == logs[type][e][b]['GW2Raidar']['id']:
                            raidar_link = 'https://www.gw2raidar.com/encounter/' + res.json()['results'][pos]['url_id']
                            logs[type][e][b]['GW2Raidar']['link'] = raidar_link
                            if not pos < 0:
                                pos -= 1
                        elif counter == 6:
                            await ctx.send('ERROR :robot: : The logs were unsuccessfully analyzed within the time frame.')
                            return await self.clear_raidar(ctx, type)
                        else:
                            print('The logs have not been analyzed. Retrying in 5 min: ' + str(counter) + '...')
                            time.sleep(300)
                            counter += 1
                            return await self.update_raidar(ctx, type, counter, length)

    async def clear_raidar(self, ctx, type: str):
        for e in logs[type]:
            for b in logs[type][e]:
                logs[type][e][b]['GW2Raidar']['link'] = 'about:blank'
                    
    async def print_logs(self, ctx, type: str, name: str):
        title = '__' + name + ' | ' + str(datetime.date.today()) + '__'
        embed = discord.Embed(title=title, colour=0xb30000)
        embed.set_footer(text='Created by Phantom#4985 | PhantomSoulz.2419')
        embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/gwwikia/images/4/4d/Guild_Wars_2_Dragon_logo.jpg/revision/latest?cb=20090825055046')
        for e in logs[type]:
            out = ''
            name = e + ':'
            no_link = 0
            for b in logs[type][e]:
                if logs[type][e][b]['dps.report'] == 'about:blank' and logs[type][e][b]['GW2Raidar']['link'] == 'about:blank':
                    no_link += 1
                    continue
                boss = b
                if boss == 'Nightmare Oratuss':
                    boss = 'Siax'
                else:
                    split = boss.split(' ')
                    if len(split) > 1:
                        if split[1] == 'the' or split[1] == 'of' or split[1] == 'Gabrel':
                            boss = split[0]
                out += boss + '  |  ' + '[dps.report](' + logs[type][e][b]['dps.report'] + ')  |  [GW2Raidar](' + logs[type][e][b]['GW2Raidar']['link'] + ')\n'
            if no_link == len(logs[type][e]):
                continue
            embed.add_field(name=name, value=out, inline=False)
            
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Arcdps(bot))