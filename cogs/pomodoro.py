import os
import pytz
import asyncio
import discord
from datetime import date, datetime
from motor import motor_asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('MONGODB_TOKEN')
tz = pytz.timezone('Europe/Berlin')


class PomodoroCog(commands.Cog, name='Main Commands'):
    
    def __init__(self, bot):
        self.bot = bot
        self.db = motor_asyncio.AsyncIOMotorClient(TOKEN)["discord"]["pomodoro"]

    @commands.command(aliases=['oi'], help='Check if bot is alive')
    async def hello(self, ctx):
        await ctx.send("I'm alive")

    @commands.command(aliases=['info'], help='Show study stats')
    async def stats(self, ctx):
        update_info(ctx)
        user_id = ctx.message.author.id
        user = await self.db.find_one({"user_id": user_id})
        time_today = round(user['date_logged'][-1][1])
        embed = discord.Embed(title=':books: Study Stats', description='\u200b',color=12320855)
        embed.add_field(name=':writing_hand: Total Time', value=f"{round(user['total_time'] / 60)} hours")
        embed.add_field(name=":partly_sunny: Today's Session", value=f"{time_today} minutes")
        await ctx.send(embed=embed)

    @commands.command(help='Remind user [< remindme 20 minutes]')
    async def remindme(self, ctx, duration:int, time):
        userid = '<@{}>'.format(ctx.message.author.id)
        if time == ["hours", "hour", "hr"]:
            duration = duration*60
        elif time in ["minutes", "minute", "min", "mins"]:
            pass
        else:
            return await ctx.send('Invalid argument')
        try:
            if duration < 0:
                await ctx.send('Must be a real number, plese')
            elif duration > 300:
                await ctx.send("Under 300 minutes, please")
            else:
                await ctx.send(f"Ok, will remind you in {duration} {time}.")
                await asyncio.sleep(duration*60)
                await ctx.send(f"{userid} timer's up!")

        except ValueError:
            await ctx.send('Must be a number!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel_id = [435126680722604036, 780238348802981928, 780238348802981929]

        user = await self.db.find_one({"user_id": member.id})
        time_now = datetime.today()
        date_now = time_now.strftime("%m/%d/%Y")

        if user is None:
            date_log = [[date_now, 0]]
            document = {"user_id": member.id, 'nick': member.name, 'total_time': 0, 'enter_time': time_now, 'studying': False, 'date_logged': date_log}
            await self.db.insert_one(document)
        else:
            new_day = tz.localize(user['enter_time']).date() < tz.localize(time_now).date()
        
        if after.channel:
            if after.channel.id in channel_id:
                await self.db.update_one({"user_id": member.id}, {"$set": {'enter_time': time_now}})
                await self.db.update_one({"user_id": member.id}, {"$set": {'studying': True}})
                if user and new_day:
                        await self.db.update_one({"user_id": member.id}, {"$set": {'total_time_today': 0}})
                        await self.db.update_one({"user_id": member.id}, {"$push": {'date_logged': [date_now, 0]}})
                else:
                    print("it's still the same day")
        else:
            if before.channel.id in channel_id:
                user = await self.db.find_one({"user_id": member.id})
                if user['studying'] is True:
                    delta_time = round((time_now - user['enter_time']).total_seconds() / 60)
                    new_time = user['date_logged'][-1]
                    new_time[1] += delta_time
                    if delta_time > 1:
                        await self.db.update_one({"user_id": member.id}, {"$inc": {'total_time': delta_time}})
                        await self.db.update_one({"user_id": member.id}, {"$pop": {'date_logged': 1}})
                        await self.db.update_one({"user_id": member.id}, {"$push": {'date_logged': new_time}})
                        await self.bot.get_channel(844625911411245117).send(f"{member.name} studied for {delta_time} minutes!")
                    await self.db.update_one({"user_id": member.id}, {"$set": {'studying': False}})

def setup(bot):
    bot.add_cog(PomodoroCog(bot))