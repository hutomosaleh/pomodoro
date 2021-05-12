from discord.ext import commands


class PomodoroCog(commands.Cog, name='Main Commands'):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['oi'], help='Check if bot is alive')
    async def hello(self, ctx):
        await ctx.send("I'm alive")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        channel_id = [435126680722604036]
        if after.channel:
            print(f"Someone went inside channel {after.channel.id}")
            if after.channel.id in channel_id:
                await member.guild.system_channel.send(f"ID: {member.id} joined the VC on {after.channel.id}!")
                #do whatever you want here

def setup(bot):
    bot.add_cog(PomodoroCog(bot))