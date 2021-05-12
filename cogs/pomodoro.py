from discord.ext import commands


class PomodoroCog(commands.Cog, name='Main Commands'):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['oi'], help='Check if bot is alive')
    async def hello(self, ctx):
        await ctx.send("I'm alive")

def setup(bot):
    bot.add_cog(PomodoroCog(bot))