import json
import requests
import calendar
import datetime
import time
import glob
import os
import copy
import re
from tkinter import filedialog
from tkinter import *

import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from selenium import webdriver
import settings.config

class Arcdps:
    def __init__(self, bot):
        self.bot = bot
        self.logs_order = {}
        self.show_time = False
        self.show_aa = False
        self.num_logs = 0
        
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
                target = await ctx.send('ERROR :robot: : GW2Raidar login failed.')
                self.bot.clear_list.append(target)
                return
            else:
                token = res.json()['token']
                key['user']['key'] = 'Token {}'.format(token)
                self.bot.owner_key = key['user']['key']
        key['user']['id'] = ctx.author.id
        self.bot.owner_id = ctx.author.id
        key['user']['name'] = ctx.author.name
        await self.bot.update_status(key['user']['name'])
        
        while len(self.bot.owner_filepath) == 0:
            out = 'Please use the file explorer to select your arcdps.cbtlogs folder.'
            try:
                await ctx.author.send(out)
            except discord.Forbidden:
                target = await ctx.send(out)
                self.bot.clear_list.append(target)
            root = Tk()
            root.withdraw()
            key['user']['filepath'] = filedialog.askdirectory(initialdir = "/", title = "Select your arcdps.cbtlogs folder")
            self.bot.owner_filepath = key['user']['filepath']
        
        with open('cogs/data/logs.json', 'w') as key_file:
            json.dump(key, key_file, indent=4)
        target = await ctx.send('Login successful ✅ : Ready to upload logs.')
        self.bot.clear_list.append(target)
        
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
            target = await ctx.send('You do not have permission to use the bot currently. Only the current user may use the bot.')
            self.bot.clear_list.append(target)
            return
        if len(self.bot.owner_filepath) == 0:
            target = await ctx.send('No file path found. Please log in and select your arcdps.cbtlogs folder.')
            self.bot.clear_list.append(target)
            return
        if not type == 'raids' and not type == 'fractals':
            target = await ctx.send('Please indicate whether you want to upload `raids` or `fractals` logs.')
            self.bot.clear_list.append(target)
            return 
        
        self.__init__(self.bot)
        i = 0
        title = []
        while i < len(argv):
            if argv[i] == '--time':
                self.show_time = True
                i += 1
            elif argv[i] == '--num':
                if i == len(argv)-1:
                    target = await ctx.send('Please enter the number of logs for the `--num` flag.')
                    self.bot.clear_list.append(target)
                    return
                try:
                    self.num_logs = int(argv[i+1])
                    if self.num_logs <= 0:
                        target = await ctx.send('Invalid number of logs for the `--num` flag.')
                        self.bot.clear_list.append(target)
                        return
                    i += 2
                except ValueError:
                    target = await ctx.send('Invalid number of logs for the `--num` flag.')
                    self.bot.clear_list.append(target)
                    return
            elif argv[i] == '--aa':
                self.show_aa = True
                i += 1
            else:
                title.append(argv[i])
                i += 1
        mode, lang = await self.set_logs_order(ctx, type)
        
        logs_length = 0
        error_logs = 0
        for e in self.logs_order:
            for b in self.logs_order[e]:
                print('------------------------------')
                logs_length += 1
                path = '{0}/{1}/'.format(self.bot.owner_filepath, self.logs[type][e][b]['name'][lang])
                if not os.path.exists(path):
                    target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: BLOODSTONE`'.format(b))
                    self.bot.clear_list.append(target)
                    error_logs += 1
                    continue
                all_files = []
                for root, dir, files in os.walk(path):
                    for file in files:
                        file_name, file_ext = os.path.splitext(file)
                        if file_ext == '.zevtc' or file_ext == '.evtc' or os.path.splitext(file_name)[1] == '.evtc':
                            file_path = os.path.join(root, file)
                            modified_date = os.path.getmtime(file_path)
                            all_files.append((file_path, modified_date))
                if len(all_files) == 0:
                    target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: EMPYREAL`'.format(b))
                    self.bot.clear_list.append(target)
                    error_logs += 1
                    continue
                elif len(all_files) < self.num_logs:
                    target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: DRAGONITE`'.format(b))
                    self.bot.clear_list.append(target)
                    error_logs += 1
                    continue
                all_files.sort(key=lambda x: x[1], reverse=True)
                if mode == 'dps.report' and self.num_logs > 0:
                    latest_files = [x[0] for x in all_files[:self.num_logs]]
                    latest_files.reverse()
                latest_file = all_files[0][0]
                self.logs[type][e][b]['filename'] = os.path.basename(latest_file)
                
                if mode == 'dps.report' or mode == 'Both':
                    print('Uploading {}: dps.report...'.format(b))
                    dps_endpoint = 'https://dps.report/uploadContent?json=1&generator=ei'
                    if self.show_aa:
                        dps_endpoint += '&rotation_weap1=1'
                        
                    async def get_time(browser, count):
                        page = browser.execute_script("return document.body.innerHTML")
                        soup = BeautifulSoup(page, 'html.parser')
                        block = soup.select('div.ml-3.d-flex div.mb-2')
                        if len(block) == 0:
                            if count <= 0:
                                target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: DWAYNA`'.format(b))
                            else:
                                target = await ctx.send('ERROR :robot: : an error has occurred with {0}({1}). `Error Code: LYSSA`'.format(b, count))
                                self.logs[type][e][b]['duration'].append('ERROR')
                            self.bot.clear_list.append(target)
                        else:
                            duration = block[-1].get_text()
                            time = re.split('[-:]', duration)
                            duration = time[1].strip()
                            if count <= 0:
                                self.logs[type][e][b]['duration'] = duration
                            else:
                                self.logs[type][e][b]['duration'].append(duration)
                        
                    if mode == 'dps.report' and self.num_logs > 0:
                        self.logs[type][e][b]['dps.report'] = []
                        if self.show_time:
                            self.logs[type][e][b]['duration'] = []
                        error_multi_logs = 0
                        for count, lf in enumerate(latest_files, 1):
                            with open(lf, 'rb') as file:
                                files = {'file': file}
                                res = requests.post(dps_endpoint, files=files)
                                if not res.status_code == 200:
                                    target = await ctx.send('ERROR :robot: : an error has occurred with {0}({1}). `Error Code: LYSSA`'.format(b, count))
                                    self.bot.clear_list.append(target)
                                    self.logs[type][e][b]['dps.report'].append('about:blank')
                                    error_multi_logs += 1
                                    continue
                                else:
                                    log = res.json()['permalink']
                                    self.logs[type][e][b]['dps.report'].append(log)
                                    if self.show_time:
                                        try:
                                            options = webdriver.ChromeOptions()
                                            options.add_argument('--headless')
                                            browser = webdriver.Chrome(options=options)
                                            browser.get(log)
                                            await get_time(browser, count)
                                            browser.quit()
                                        except IOError as e:
                                            try:
                                                options = webdriver.FirefoxOptions()
                                                options.add_argument('--headless')
                                                browser = webdriver.Firefox(options=options)
                                                browser.get(log)
                                                await get_time(browser, count)
                                                browser.quit()
                                            except IOError as e:
                                                target = await ctx.send('ERROR :robot: : an error has occurred with {0}({1}). `Error Code: GRENTH`'.format(b, count))
                                                self.bot.clear_list.append(target)
                                                self.logs[type][e][b]['duration'].append('ERROR')
                        if error_multi_logs == len(latest_files):
                            error_logs += 1
                            continue
                    else:
                        with open(latest_file, 'rb') as file:
                            files = {'file': file}
                            res = requests.post(dps_endpoint, files=files)
                            if not res.status_code == 200:
                                target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: LYSSA`'.format(b))
                                self.bot.clear_list.append(target)
                                error_logs += 1
                                continue
                            else:
                                self.logs[type][e][b]['dps.report'] = res.json()['permalink']
                                if self.show_time:
                                    try:
                                        options = webdriver.ChromeOptions()
                                        options.add_argument('--headless')
                                        browser = webdriver.Chrome(options=options)
                                        browser.get(self.logs[type][e][b]['dps.report'])
                                        await get_time(browser, 0)
                                        browser.quit()
                                    except IOError as e:
                                        try:
                                            options = webdriver.FirefoxOptions()
                                            options.add_argument('--headless')
                                            browser = webdriver.Firefox(options=options)
                                            browser.get(self.logs[type][e][b]['dps.report'])
                                            await get_time(browser, 0)
                                            browser.quit()
                                        except IOError as e:
                                            target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: GRENTH`'.format(b))
                                            self.bot.clear_list.append(target)                       
                    print('Uploaded {}: dps.report'.format(b))

                if mode == 'GW2Raidar' or mode == 'Both':
                    print('Uploading {}: GW2Raidar...'.format(b))
                    if len(self.bot.owner_key) == 0:
                        target = await ctx.send('ERROR :robot: : Key not found. Please log into GW2Raidar before uploading.')
                        self.bot.clear_list.append(target)
                        return
                    raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters/new'
                    with open(latest_file, 'rb') as file:
                        files = {'file': file}
                        res = requests.put(raidar_endpoint, headers={'Authorization': self.bot.owner_key}, files=files)
                        if not res.status_code == 200:
                            if res.status_code == 401:
                                target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: RYTLOCK`'.format(b))
                                self.bot.clear_list.append(target)
                                error_logs += 1
                                continue
                            elif res.status_code == 400:
                                target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: ZOJJA`'.format(b))
                                self.bot.clear_list.append(target)
                                error_logs += 1
                                continue
                            else:
                                target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: SNAFF`'.format(b))
                                self.bot.clear_list.append(target)
                                error_logs += 1
                                continue
                        else:
                            self.logs[type][e][b]['GW2Raidar']['success'] = True
                    print('Uploaded {}: GW2Raidar'.format(b))
        
        if not error_logs == logs_length:
            print('------------------------------')
            if mode == 'GW2Raidar' or mode == 'Both':
                counter = 0
                await self.update_raidar(ctx, type, counter, logs_length, mode)
            await self.print_logs(ctx, type, ' '.join(title), mode)
        
    async def set_logs_order(self, ctx, type: str):
        temp_logs = copy.deepcopy(self.logs)
        out = 'Type of the `number` of your language.\n```md\n1. English\n2. German\n3. French\n```'
        try:
            message = await ctx.author.send(out)
        except discord.Forbidden:
            target = await ctx.send('I do not have permission to DM you. Please enable this in the future.')
            self.bot.clear_list.append(target)
            return
        
        def m_check(m):
            return m.author == ctx.author and m.channel == message.channel
            
        ans = await self.bot.wait_for('message', check=m_check)
        await message.delete()
        lang_num = ans.content
        
        def switch(x):
            return {
                '1': (0, 'English'),
                '2': (1, 'German'),
                '3': (2, 'French')
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
        
    async def update_raidar(self, ctx, type: str, counter: int, length: int, mode: str):
        if length == 0:
            return
   
        if len(self.bot.owner_key) == 0:
            target = await ctx.send('ERROR :robot: : Key not found. Please log into GW2Raidar before uploading.')
            self.bot.clear_list.append(target)
            return
        raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters?limit={}'.format(str(length))
        res = requests.get(raidar_endpoint, headers={'Authorization': self.bot.owner_key})
        if not res.status_code == 200:
            target = await ctx.send('ERROR :robot: : an error has occurred. `Error Code: CAITHE`')
            self.bot.clear_list.append(target)
            return
        else:   
            for e in self.logs_order:
                for b in self.logs_order[e]:
                    if not self.logs[type][e][b]['GW2Raidar']['success'] or not self.logs[type][e][b]['GW2Raidar']['link'] == 'about:blank':
                        continue
                    for encounter in res.json()['results']:
                        if self.logs[type][e][b]['filename'] in encounter['filename']:
                            raidar_link = 'https://www.gw2raidar.com/encounter/{}'.format(encounter['url_id'])
                            self.logs[type][e][b]['GW2Raidar']['link'] = raidar_link
                            if self.show_time and mode == 'GW2Raidar':
                                raidar_json = '{}.json'.format(raidar_link)
                                json_res = requests.get(raidar_json)
                                if not json_res.status_code == 200:
                                    target = await ctx.send('ERROR :robot: : an error has occurred with {}. `Error Code: LOGAN`'.format(b))
                                    self.bot.clear_list.append(target)
                                else:
                                    seconds = json_res.json()['encounter']['phases']['All']['duration']
                                    m, s = divmod(seconds, 60)
                                    duration = '%02d:%06.3f' % (m, s)
                                    self.logs[type][e][b]['duration'] = duration
                            break
                    if not self.logs[type][e][b]['GW2Raidar']['link'] == 'about:blank':
                        continue
                    elif counter == 6:
                        target = await ctx.send('ERROR :robot: : The logs were unsuccessfully analyzed within the time frame.')
                        self.bot.clear_list.append(target)
                        return
                    else:
                        print('The logs have not been analyzed. Retrying in 2.5 min: {}...'.format(str(counter)))
                        time.sleep(150)
                        counter += 1
                        return await self.update_raidar(ctx, type, counter, length, mode)
                    
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
                    if self.num_logs > 0:
                        if not boss_e is None:
                            out += '{}  '.format(boss_e)
                        out += '**{}**  '.format(boss)
                        for count, log in enumerate(self.logs[type][e][b]['dps.report'], 1):
                            if self.show_time and 'duration' in self.logs[type][e][b] and not self.logs[type][e][b]['duration'][count-1] == 'ERROR':
                                out += '|  [{0}]({1})  '.format(self.logs[type][e][b]['duration'][count-1], log)
                            else:
                                out += '|  [Log {0}]({1})  '.format(count, log)
                        out += '\n'
                    else:
                        if not count == no_link and not self.show_time:
                            out += '  |  '
                        if not boss_e is None:
                            out += '{}  '.format(boss_e)
                        out += '[**{0}**]({1})'.format(boss, self.logs[type][e][b]['dps.report'])
                        if self.show_time and not 'duration' in self.logs[type][e][b]:
                            out += '\n'
                elif mode == 'GW2Raidar':
                    if not count == no_link and not self.show_time:
                        out += '  |  '
                    if not boss_e is None:
                        out += '{}  '.format(boss_e)
                    out += '[**{0}**]({1})'.format(boss, self.logs[type][e][b]['GW2Raidar']['link'])
                    if self.show_time and not 'duration' in self.logs[type][e][b]:
                        out += '\n'
                elif mode == 'Both':
                    if not boss_e is None:
                        out += '{}  '.format(boss_e)
                    out += '**{0}**  |  [dps.report]({1})  ·  [GW2Raidar]({2})'.format(boss, self.logs[type][e][b]['dps.report'], self.logs[type][e][b]['GW2Raidar']['link'])
                    if not self.show_time or not 'duration' in self.logs[type][e][b]:
                        out += '\n'
                if self.show_time and 'duration' in self.logs[type][e][b] and not isinstance(self.logs[type][e][b]['duration'], list):
                    out += '  |  **Time**: {}\n'.format(self.logs[type][e][b]['duration'])
                
            if no_link == len(self.logs[type][e]):
                continue
            embed.add_field(name=name, value=out, inline=False)
            
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Arcdps(bot))