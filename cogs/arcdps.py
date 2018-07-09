import json
import requests
import datetime
import time
import glob
import os
import copy

import discord
from discord.ext import commands
import settings.config

class Arcdps:
    def __init__(self, bot):
        self.bot = bot
        self.logs_order = {}
        
        with open('cogs/data/logs.json', 'r') as logs_data:
            self.logs = json.load(logs_data)
    
    @commands.command()
    async def login(self, ctx, username: str, password: str):
        guild = ctx.guild
        if guild is None:
            has_perms = False
        else:
            has_perms = ctx.channel.permissions_for(guild.me).manage_messages
        if has_perms:
            await ctx.message.delete()
        else:
            await ctx.send('I do not have permissions to delete messages. Please enable this in the future.')
    
        raidar_endpoint = 'https://www.gw2raidar.com/api/v2/token'
        cred = {'username': username, 'password': password}
        res = requests.post(raidar_endpoint, data=cred)
        if not res.status_code == 200:
            return await ctx.send('ERROR :robot: : GW2Raidar login failed.')
        else:
            token = res.json()['token']
            with open('cogs/data/logs.json', 'r') as key_file:
                key = json.load(key_file)
            key['key'] = 'Token {}'.format(token)
            with open('cogs/data/logs.json', 'w') as key_file:
                json.dump(key, key_file, indent=4)
            await ctx.send('Login successful ✅ : Ready to upload logs.')
        
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
        
        self.__init__(self.bot)
        await self.set_logs_order(ctx, type)
        
        logs_length = 0
        error_logs = 0
        for e in self.logs_order:
            for b in self.logs_order[e]:
                logs_length += 1
                path = '{0}{1}/*'.format(os.path.expanduser('~/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/'), b)
                all_files = glob.glob(path)
                if len(all_files) == 0:
                    await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: BLOODSTONE`'.format(b))
                    error_logs += 1
                    continue 
                latest_file = max(all_files, key=os.path.getmtime)
                while os.path.isdir(latest_file):
                    path = '{}/*'.format(latest_file)
                    all_files = glob.glob(path)
                    if len(all_files) == 0:
                        await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: BLOODSTONE`'.format(b))
                        error_logs += 1
                        continue
                    latest_file = max(all_files, key=os.path.getmtime)
                
                print('Uploading {}: dps.report...'.format(b))
                dps_endpoint = 'https://dps.report/uploadContent?json=1&generator=ei'
                with open(latest_file, 'rb') as file:
                    files = {'file': file}
                    res = requests.post(dps_endpoint, files=files)
                    if not res.status_code == 200:
                        await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: DHUUMFIRE`'.format(b))
                        error_logs += 1
                        continue
                    else:
                        self.logs[type][e][b]['dps.report'] = res.json()['permalink']
                print('Uploaded {}: dps.report'.format(b))

                print('Uploading {}: GW2Raidar...'.format(b))
                with open('cogs/data/logs.json', 'r') as key_file:
                    key = json.load(key_file)
                    if len(key['key']) == 0:
                        await ctx.send('ERROR :robot: : Key not found. Please log into GW2Raidar before uploading.')
                        error_logs += 1
                        continue
                    else:
                        auth = key['key']
                raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters/new'
                with open(latest_file, 'rb') as file:
                    files = {'file': file}
                    res = requests.put(raidar_endpoint, headers={'Authorization': auth}, files=files)
                    if not res.status_code == 200:
                        if res.status_code == 401:
                            await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: RYTLOCK`'.format(b))
                            error_logs += 1
                            continue
                        elif res.status_code == 400:
                            await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: ZOJJA`'.format(b))
                            error_logs += 1
                            continue
                        else:
                            await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: SNAFF`'.format(b))
                            error_logs += 1
                            continue
                    else:
                        self.logs[type][e][b]['GW2Raidar']['success'] = True
                print('Uploaded {}: GW2Raidar'.format(b))
                print('------------------------------')
        
        if not error_logs == logs_length:
            counter = 0
            await self.update_raidar(ctx, type, counter, logs_length)
            await self.print_logs(ctx, type, name)
        
    async def set_logs_order(self, ctx, type: str):
        temp_logs = copy.deepcopy(self.logs)
        while True:
            e_order = 0
            out = 'Type the number of the wing/scale that you wish to upload.\n```md\n'
            if len(temp_logs[type]) == 0:
                break

            event = []
            for count, e in enumerate(temp_logs[type], 1):
                out += '{0}. {1}\n'.format(count, e)
                event.append(e)
            out += '\n[x]: [Confirm Wing/Scale Order]\n```'
            try:
                message = await ctx.author.send(out)
            except discord.Forbidden:
                return await ctx.send('I do not have permissions to DM you. Please enable this in the future.')
                
            def m_check(m):
                return m.author == ctx.author and m.channel == message.channel
                
            ans = await self.bot.wait_for('message', check=m_check)
            await message.delete()
            e_order = ans.content
            if e_order == 'x':
                break
            e_pos = int(e_order) - 1
            self.logs_order[event[e_pos]] = []
            
            while True:
                b_order = 0
                out = 'Type the number of the boss that you wish to upload.\n```md\n'
                if len(temp_logs[type][event[e_pos]]) == 0:
                    break

                boss = []
                for count, b in enumerate(temp_logs[type][event[e_pos]], 1):
                    if b == 'Nightmare Oratuss':
                        out += '{}. Siax the Corrupted\n'.format(count)
                    else:
                        out += '{0}. {1}\n'.format(count, b)
                    boss.append(b)
                out += '\n0. [Upload All Bosses in Order]\n[x]: [Confirm Boss Order]\n```'
                message = await ctx.author.send(out)
                
                ans = await self.bot.wait_for('message', check=m_check)
                await message.delete()
                b_order = ans.content
                if b_order == 'x':
                    break
                elif int(b_order) == 0:
                    self.logs_order[event[e_pos]] = boss
                    break
                b_pos = int(b_order) - 1
                self.logs_order[event[e_pos]].append(boss[b_pos])
                
                del temp_logs[type][event[e_pos]][boss[b_pos]]            
            del temp_logs[type][event[e_pos]]

        print_order = ''
        for e in self.logs_order:
            print_order += '{0}: {1}\n'.format(e, self.logs_order[e])
        message = await ctx.author.send('Your selected log order is:\n```{}\n✅ to confirm, ❌ to cancel```'.format(print_order))
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        
        def r_check(r, user):
            return user == ctx.author and r.count > 1
            
        ans, user = await self.bot.wait_for('reaction_add', check=r_check)
        if str(ans.emoji) == '❌':
            self.logs_order = {}
        await message.delete()
        
    async def update_raidar(self, ctx, type: str, counter: int, length: int):
        if length == 0:
            return
   
        with open('cogs/data/logs.json', 'r') as key_file:
            key = json.load(key_file)
            if len(key['key']) == 0:
                return await ctx.send('ERROR :robot: : Key not found. Please log into GW2Raidar before uploading.')
            else:
                auth = key['key']
        raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters?limit={}'.format(str(length))
        res = requests.get(raidar_endpoint, headers={'Authorization': auth})
        if not res.status_code == 200:
            return await ctx.send('ERROR :robot: : an error has occurred. `Error Code: CAITHE`'.format(b))
        else:
            pos = length - 1    
            for e in self.logs_order:
                for b in self.logs_order[e]:
                    if not self.logs[type][e][b]['GW2Raidar']['success']:
                        continue

                    if res.json()['results'][pos]['area_id'] == self.logs[type][e][b]['GW2Raidar']['id']:
                        raidar_link = 'https://www.gw2raidar.com/encounter/{}'.format(res.json()['results'][pos]['url_id'])
                        self.logs[type][e][b]['GW2Raidar']['link'] = raidar_link
                        if not pos < 0:
                            pos -= 1
                    elif counter == 6:
                        await ctx.send('ERROR :robot: : The logs were unsuccessfully analyzed within the time frame.')
                        return await self.clear_raidar(ctx, type)
                    else:
                        print('The logs have not been analyzed. Retrying in 5 min: {}...'.format(str(counter)))
                        time.sleep(300)
                        counter += 1
                        return await self.update_raidar(ctx, type, counter, length)

    async def clear_raidar(self, ctx, type: str):
        for e in self.logs[type]:
            for b in self.logs[type][e]:
                self.logs[type][e][b]['GW2Raidar']['link'] = 'about:blank'
                    
    async def print_logs(self, ctx, type: str, name: str):
        title = '__{0} | {1}__'.format(name, str(datetime.date.today()))
        embed = discord.Embed(title=title, colour=0xb30000)
        embed.set_footer(text='Created by Phantom#4985 | PhantomSoulz.2419')
        embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/gwwikia/images/4/4d/Guild_Wars_2_Dragon_logo.jpg/revision/latest?cb=20090825055046')
        for e in self.logs[type]:
            out = ''
            name = '{}:'.format(e)
            no_link = 0
            for b in self.logs[type][e]:
                if self.logs[type][e][b]['dps.report'] == 'about:blank' and self.logs[type][e][b]['GW2Raidar']['link'] == 'about:blank':
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
                out += '{0}  |  [dps.report]({1})  |  [GW2Raidar]({2})\n'.format(boss, self.logs[type][e][b]['dps.report'], self.logs[type][e][b]['GW2Raidar']['link'])
            if no_link == len(self.logs[type][e]):
                continue
            embed.add_field(name=name, value=out, inline=False)
            
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Arcdps(bot))