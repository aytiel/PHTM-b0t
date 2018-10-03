import json
import requests
import calendar
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
        self.show_time = False
        
        with open('cogs/data/logs.json', 'r') as logs_data:
            self.logs = json.load(logs_data)
    
    @commands.command()
    async def login(self, ctx, username=None, password=None):
        guild = ctx.guild
        if guild is None:
            has_perms = False
        else:
            has_perms = ctx.channel.permissions_for(guild.me).manage_messages
        if has_perms:
            await ctx.message.delete()
        else:
            await ctx.send('I do not have permissions to delete messages. Please enable this in the future.')

        with open('cogs/data/logs.json', 'r') as key_file:
            key = json.load(key_file)
        if not username is None and not password is None:
            raidar_endpoint = 'https://www.gw2raidar.com/api/v2/token'
            cred = {'username': username, 'password': password}
            res = requests.post(raidar_endpoint, data=cred)
            if not res.status_code == 200:
                return await ctx.send('ERROR :robot: : GW2Raidar login failed.')
            else:
                token = res.json()['token']
                key['user']['key'] = 'Token {}'.format(token)
                self.bot.owner_key = key['user']['key']
        key['user']['id'] = ctx.author.id
        self.bot.owner_id = ctx.author.id
        key['user']['name'] = ctx.author.name
        await self.bot.update_status(key['user']['name'])
        with open('cogs/data/logs.json', 'w') as key_file:
            json.dump(key, key_file, indent=4)
        await ctx.send('Login successful ✅ : Ready to upload logs.')
        
    @commands.command()
    async def upload(self, ctx, type: str, *argv):
        guild = ctx.guild
        if guild is None:
            has_perms = False
        else:
            has_perms = ctx.channel.permissions_for(guild.me).manage_messages
        if has_perms:
            await ctx.message.delete()
        else:
            await ctx.send('I do not have permissions to delete messages. Please enable this in the future.')
        
        if self.bot.owner_id == 0 or not self.bot.owner_id == ctx.author.id:
            return await ctx.send('You do not have permission to use the bot currently. Only the current user may use the bot.')
        if not type == 'raids' and not type == 'fractals':
            return await ctx.send('Please indicate whether you want to upload `raids` or `fractals` logs.')
        
        self.__init__(self.bot)
        if len(argv) > 0:
            if argv[len(argv)-1] == '--time':
                argv = argv[:(len(argv)-1)]
                self.show_time = True
        mode, lang = await self.set_logs_order(ctx, type)
        
        logs_length = 0
        error_logs = 0
        for e in self.logs_order:
            for b in self.logs_order[e]:
                print('------------------------------')
                logs_length += 1
                path = '{0}{1}/*'.format(os.path.expanduser('~/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/'), self.logs[type][e][b]['name'][lang])
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
                        break
                    latest_file = max(all_files, key=os.path.getmtime)
                if len(all_files) == 0:
                    await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: EMPYREAL`'.format(b))
                    error_logs += 1
                    continue
                self.logs[type][e][b]['filename'] = os.path.basename(latest_file)
                
                if mode == 'dps.report' or mode == 'Both':
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

                if mode == 'GW2Raidar' or mode == 'Both':
                    print('Uploading {}: GW2Raidar...'.format(b))
                    if len(self.bot.owner_key) == 0:
                        return await ctx.send('ERROR :robot: : Key not found. Please log into GW2Raidar before uploading.')
                    raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters/new'
                    with open(latest_file, 'rb') as file:
                        files = {'file': file}
                        res = requests.put(raidar_endpoint, headers={'Authorization': self.bot.owner_key}, files=files)
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
        
        if not error_logs == logs_length:
            print('------------------------------')
            if mode == 'GW2Raidar' or mode == 'Both':
                counter = 0
                await self.update_raidar(ctx, type, counter, logs_length)
            await self.print_logs(ctx, type, ' '.join(argv), mode)
        
    async def set_logs_order(self, ctx, type: str):
        temp_logs = copy.deepcopy(self.logs)
        out = 'Type of the `number` of your language.\n```md\n1. English\n2. German\n```'
        try:
            message = await ctx.author.send(out)
        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')
        
        def m_check(m):
            return m.author == ctx.author and m.channel == message.channel
            
        ans = await self.bot.wait_for('message', check=m_check)
        await message.delete()
        lang_num = ans.content
        
        def switch(x):
            return {
                '1': (0, 'English'),
                '2': (1, 'German')
            }.get(x, (0, 'English'))
            
        lang = switch(lang_num)
            
        out = 'Type the `number` of the parser that you wish to upload to.\n```md\n1. dps.report\n2. GW2Raidar\n3. Both\n```'
        message = await ctx.author.send(out)
            
        ans = await self.bot.wait_for('message', check=m_check)
        await message.delete()
        mode_num = ans.content
        
        def switch(x):
            return {
                '1': 'dps.report',
                '2': 'GW2Raidar',
                '3': 'Both'
            }.get(x, 'Both')
            
        mode = switch(mode_num)
            
        while True:
            logs_len = len(self.logs_order)
            out = 'Type the `number` of the wing/scale that you wish to upload'
            if logs_len == 0:
                out += ' or `0` to upload all of the bosses in all of the wings/scales.\n'
            else:
                out += '.\n'
            out += 'Type `x` to confirm your selection.\n```md\n'
            if len(temp_logs[type]) == 0:
                break

            event = []
            for count, e in enumerate(temp_logs[type], 1):
                out += '{0}. {1}\n'.format(count, e)
                event.append(e)
            if logs_len == 0:
                out += '\n0. [Upload All Bosses]'
            out += '\n[x]: [Confirm Wing/Scale Order]\n```'
            message = await ctx.author.send(out)
                
            ans = await self.bot.wait_for('message', check=m_check)
            await message.delete()
            e_order = ans.content
            if e_order == 'x':
                break
            try:
                if int(e_order) == 0 and logs_len == 0:
                    self.logs_order = {e: [boss for boss in temp_logs[type][e]] for e in temp_logs[type]}
                    break

                e_pos = int(e_order) - 1
                if e_pos < 0 or e_pos >= len(event):
                    continue
                self.logs_order[event[e_pos]] = []
            except ValueError:
                continue
            
            while True:
                event_len = len(self.logs_order[event[e_pos]])
                out = 'Type the `number` of the boss that you wish to upload'
                if event_len == 0:
                    out += ' or `0` to upload all of the bosses.\n'
                else:
                    out += '.\n'
                out += 'Type `x` to confirm your selection.\n```md\n'
                if len(temp_logs[type][event[e_pos]]) == 0:
                    break

                boss = []
                for count, b in enumerate(temp_logs[type][event[e_pos]], 1):
                    out += '{0}. {1}\n'.format(count, b)
                    boss.append(b)
                if event_len == 0:
                    out += '\n0. [Upload All Bosses]'
                out += '\n[x]: [Confirm Boss Order]\n```'
                message = await ctx.author.send(out)
                
                ans = await self.bot.wait_for('message', check=m_check)
                await message.delete()
                b_order = ans.content
                if b_order == 'x':
                    break
                try:
                    if int(b_order) == 0 and event_len == 0:
                        self.logs_order[event[e_pos]] = boss
                        break

                    b_pos = int(b_order) - 1
                    if b_pos < 0 or b_pos >= len(boss):
                        continue
                    self.logs_order[event[e_pos]].append(boss[b_pos])
                except ValueError:
                    continue
                
                del temp_logs[type][event[e_pos]][boss[b_pos]]            
            del temp_logs[type][event[e_pos]]
        del temp_logs

        print_order = 'Uploading to {0} in {1}...\n'.format(mode, lang[1])
        for e in self.logs_order:
            if not len(self.logs_order[e]) == 0:
                print_order += '{0}: {1}\n'.format(e, self.logs_order[e])
        message = await ctx.author.send('Your selected log order is:\n```{}\nClick ✅ to confirm, ❌ to cancel```'.format(print_order))
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        
        def r_check(r, user):
            return user == ctx.author and r.count > 1
            
        ans, user = await self.bot.wait_for('reaction_add', check=r_check)
        if str(ans.emoji) == '❌':
            self.logs_order = {}
        await message.delete()
        
        return (mode, lang[0])
        
    async def update_raidar(self, ctx, type: str, counter: int, length: int):
        if length == 0:
            return
   
        if len(self.bot.owner_key) == 0:
            return await ctx.send('ERROR :robot: : Key not found. Please log into GW2Raidar before uploading.')
        raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters?limit={}'.format(str(length))
        res = requests.get(raidar_endpoint, headers={'Authorization': self.bot.owner_key})
        if not res.status_code == 200:
            return await ctx.send('ERROR :robot: : an error has occurred. `Error Code: CAITHE`')
        else:   
            for e in self.logs_order:
                for b in self.logs_order[e]:
                    if not self.logs[type][e][b]['GW2Raidar']['success'] or not self.logs[type][e][b]['GW2Raidar']['link'] == 'about:blank':
                        continue
                    for encounter in res.json()['results']:
                        if self.logs[type][e][b]['filename'] in encounter['filename']:
                            raidar_link = 'https://www.gw2raidar.com/encounter/{}'.format(encounter['url_id'])
                            self.logs[type][e][b]['GW2Raidar']['link'] = raidar_link
                            if self.show_time:
                                raidar_json = '{}.json'.format(raidar_link)
                                json_res = requests.get(raidar_json)
                                if not json_res.status_code == 200:
                                    await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: LOGAN`'.format(b))
                                else:
                                    seconds = json_res.json()['encounter']['phases']['All']['duration']
                                    m, s = divmod(seconds, 60)
                                    duration = '%02d:%06.3f' % (m, s)
                                    self.logs[type][e][b]['duration'] = duration
                            break
                    if not self.logs[type][e][b]['GW2Raidar']['link'] == 'about:blank':
                        continue
                    elif counter == 6:
                        return await ctx.send('ERROR :robot: : The logs were unsuccessfully analyzed within the time frame.')
                    else:
                        print('The logs have not been analyzed. Retrying in 2.5 min: {}...'.format(str(counter)))
                        time.sleep(150)
                        counter += 1
                        return await self.update_raidar(ctx, type, counter, length)
                    
    async def print_logs(self, ctx, type: str, name: str, mode: str):
        if len(name) > 0:
            title = '__{0} | {1}__'.format(name, str(datetime.date.today()))
        else:
            title = '__{}__'.format(str(datetime.date.today()))
        embed = discord.Embed(title=title, colour=0xb30000)
        embed.set_footer(text='Created by Phantom#4985 | PhantomSoulz.2419')
        embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/gwwikia/images/4/4d/Guild_Wars_2_Dragon_logo.jpg/revision/latest?cb=20090825055046')
        for e in self.logs[type]:
            out = ''
            name = '{}:'.format(e)
            no_link = 0
            for count, b in enumerate(self.logs[type][e]):
                if self.logs[type][e][b]['dps.report'] == 'about:blank' and self.logs[type][e][b]['GW2Raidar']['link'] == 'about:blank':
                    no_link += 1
                    continue
                boss = b
                
                boss_e = None
                for emoji in self.bot.emoji_list:
                    if emoji.name == b.replace(' ', '_'):
                        boss_e = emoji
                        break

                if mode == 'dps.report':
                    if not count == no_link:
                        out += '  |  '
                    if not boss_e is None:
                        out += '{}  '.format(boss_e)
                    out += '[**{0}**]({1})'.format(boss, self.logs[type][e][b]['dps.report'])
                elif mode == 'GW2Raidar':
                    if not count == no_link and not self.show_time:
                        out += '  |  '
                    if not boss_e is None:
                        out += '{}  '.format(boss_e)
                    out += '[**{0}**]({1})'.format(boss, self.logs[type][e][b]['GW2Raidar']['link'])
                elif mode == 'Both':
                    if not boss_e is None:
                        out += '{}  '.format(boss_e)
                    out += '**{0}**  |  [dps.report]({1})  ·  [GW2Raidar]({2})'.format(boss, self.logs[type][e][b]['dps.report'], self.logs[type][e][b]['GW2Raidar']['link'])
                    if not self.show_time or self.logs[type][e][b]['GW2Raidar']['link'] == 'about:blank':
                        out += '\n'
                if self.show_time and 'duration' in self.logs[type][e][b]:
                    out += '  |  **Time**: {}\n'.format(self.logs[type][e][b]['duration'])
                
            if no_link == len(self.logs[type][e]):
                continue
            embed.add_field(name=name, value=out, inline=False)
            
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Arcdps(bot))