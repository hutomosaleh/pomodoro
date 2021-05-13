import os
from datetime import datetime
from motor import motor_asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('MONGODB_TOKEN')


class PomodoroCog(commands.Cog, name='Main Commands'):
    
    def __init__(self, bot):
        self.bot = bot
        self.db = motor_asyncio.AsyncIOMotorClient(TOKEN)["discord"]["pomodoro"]

    @commands.command(aliases=['oi'], help='Check if bot is alive')
    async def hello(self, ctx):
        await ctx.send("I'm alive")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel_id = [435126680722604036]
        user = await self.db.find_one({"user_id": member.id})
        if user is None:
            document = {"user_id": member.id, 'total_time': 0}
            await self.db.insert_one(document)
            await member.guild.system_channel.send(f"ID: {member.id} joined the VC on {after.channel.id}!")
        if after.channel:
            if after.channel.id in channel_id:
                await self.db.update_one({"user_id": member.id}, {"$set": {'enter_time': datetime.today()}})
                await member.guild.system_channel.send(f"ID: {member.id} joined the VC on {after.channel.id}!")
        else:
            if before.channel.id in channel_id:
                delta_time = (datetime.today() - user['enter_time']).total_seconds() / 60
                await self.db.update_one({"user_id": member.id}, {"$inc": {'total_time': delta_time}})
                await member.guild.system_channel.send(f"You just studied for {delta_time} minutes!")

def setup(bot):
    bot.add_cog(PomodoroCog(bot))