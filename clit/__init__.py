from .clit import Clit

async def setup(bot):
    await bot.add_cog(Clit())
