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
            'Vale Guardian': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Gorseval the Multifarious': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Sabetha the Saboteur': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'}
        },
        'W2': {
            'Slothasor': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Matthias Gabrel': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'}
        },
        'W3': {
            'Keep Construct': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Xera': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'}
        },
        'W4': {
            'Cairn the Indomitable': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Mursaat Overseer': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Samarog': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Deimos': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'}
        },
        'W5': {
            'Soulless Horror': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Dhuum': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'}
        }
    },
    'fractals': {
        '99CM': {
            'MAMA': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Nightmare Oratuss': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Ensolyss of the Endless Torment': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'}
        },
        '100CM': {
            'Skorvald the Shattered': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Artsariiv': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'},
            'Arkk': {'dps.report': 'about:blank', 'GW2Raidar': 'about:blank'}
        }
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
            await ctx.send('Please indicate whether you want to upload **raids** or **fractals** logs.')
            return
        
        for e in logs[type]:
            for b in logs[type][e]:
                path = 'C:/Users/atl/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/' + b + '/*'
                all_files = glob.glob(path)
                latest_file = max(all_files, key=os.path.getctime)
                if latest_file is None:
                    error = 'ERROR ?? : an error has occurred with ' + b
                    await ctx.send(error)
                    continue
                        
                dps_endpoint = 'https://dps.report/uploadContent?json=1&generator=rh'
                with open(latest_file, 'rb') as file:
                    files = {'file': file}
                    res = requests.post(dps_endpoint, files=files)
                    if not res.status_code == 200:
                        error = 'ERROR ?? : an error has occurred with ' + b
                        await ctx.send(error)
                        continue
                    else:
                        logs[type][e][b]['dps.report'] = res.json()['permalink']
                print('Uploaded ' + b + ': dps.report')
                    
                raidar_endpoint = 'https://www.gw2raidar.com/api/v2/token'
                cred = {'username': settings.config.RAIDARUSER, 'password': settings.config.RAIDARPASS}
                res = requests.post(raidar_endpoint, data=cred)
                if not res.status_code == 200:
                    error = 'ERROR ?? : an error has occurred with ' + b
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
                            error = 'ERROR ?? : an error has occurred with ' + b
                            await ctx.send(error)
                            continue
                        else:
                            raidar_endpoint = 'https://www.gw2raidar.com/api/v2/areas'
                            res = requests.get(raidar_endpoint, headers={'Authorization': auth})
                            if not res.status_code == 200:
                                error = 'ERROR ?? : an error has occurred with ' + b
                                await ctx.send(error)
                                continue
                            #else:
                            #    boss_id = None
                            #    for boss in res.json()['results']:
                            #        if boss['name'].split(' ')[0] == 'Siax' and b == 'Nightmare Oratuss':
                            #            boss_id = boss['id']
                            #            break
                            #        elif boss['name'].split(' ')[0] in b:
                            #            boss_id = boss['id']
                            #            break
                            #    if boss_id is None:
                            #        error = 'ERROR ?? : an error has occurred with ' + b
                            #        await ctx.send(error)
                            #        continue
                            #    counter = 0
                            #    await self.update_raidar(ctx, type, e, b, auth, boss_id, counter)
                print('Uploaded ' + b + ': GW2Raidar')          
                
        await self.print_logs(ctx, type, name)
        
    async def update_raidar(self, ctx, type: str, e: str, b: str, auth: str, boss_id: int, counter: int):
        raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters?limit=1'
        res = requests.get(raidar_endpoint, headers={'Authorization': auth})
        if not res.status_code == 200:
            error = 'ERROR ?? : an error has occurred with ' + b
            await ctx.send(error)
            return
        else:
            if res.json()['results'][0]['area_id'] == boss_id:
                raidar_link = 'https://www.gw2raidar.com/encounter/' + res.json()['results'][0]['url_id']
                logs[type][e][b]['GW2Raidar'] = raidar_link
                return
            elif counter == 3:
                error = 'ERROR ?? : an error has occurred with ' + b
                await ctx.send(error)
                return
            else:
                print(b + ': GW2Raidar has not been retrieved. Retrying ' + str(counter))
                time.sleep(40)
                counter += 1
                await self.update_raidar(ctx, type, e, b, auth, boss_id, counter)       
                    
    async def print_logs(self, ctx, type: str, name: str):
        title = '__' + name + ' | ' + str(datetime.date.today()) + '__'
        embed = discord.Embed(title=title, colour=0x6496e5)
        embed.set_footer(text='Created by Phantom#4985')
        embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/gwwikia/images/4/4d/Guild_Wars_2_Dragon_logo.jpg/revision/latest?cb=20090825055046')
        for e in logs[type]:
            out = ''
            name = e + ':'
            for b in logs[type][e]:
                boss = b
                if boss == 'Nightmare Oratuss':
                    boss = 'Siax'
                else:
                    split = boss.split(' ')
                    if len(split) > 1:
                        if split[1] == 'the' or split[1] == 'of' or split[1] == 'Gabrel':
                            boss = split[0]
                out += boss + '  |  ' + '[dps.report](' + logs[type][e][b]['dps.report'] + ')  |  [GW2Raidar](' + logs[type][e][b]['GW2Raidar'] + ')\n'
            embed.add_field(name=name, value=out, inline=False)
            
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Arcdps(bot))