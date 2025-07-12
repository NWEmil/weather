import discord
import random
from redbot.core import commands
from redbot.core.utils.chat_formatting import pagify

class Clit(commands.Cog):
    """Clit related commands."""

    @commands.command()
    async def clit(self, ctx, *users: discord.Member):
        """Detects user's clit size

        This is 100% accurate.
        Enter multiple users for an accurate comparison!"""
        
        if not users:
            await ctx.send_help()
            return

        # Dictionary to store user and their clit size representation
        clits = {}
        msg = ""
        
        # Save the current random state to restore later
        state = random.getstate()
        
        for user in users:
            # Use user ID as seed for consistent results
            random.seed(str(user.id))
            
            # Bot gets special treatment (largest size)
            if ctx.bot.user.id == user.id:
                length = 50
            else:
                # Generate random length between 0-30 for consistency with original
                length = random.randint(0, 30)
            
            # Create ASCII art pattern using curly braces
            # Pattern: ( {} ) for smallest, ( {{ }} ) for medium, etc.
            if length == 0:
                clit_art = "( )"
            else:
                # Create balanced curly braces pattern
                opening_braces = "{" * length
                closing_braces = "}" * length
                clit_art = f"( {opening_braces} {closing_braces} )"
            
            clits[user] = clit_art
        
        # Restore random state
        random.setstate(state)
        
        # Sort by length (from shortest to longest ASCII representation)
        clits = sorted(clits.items(), key=lambda x: len(x[1]))
        
        # Build the message
        for user, clit in clits:
            msg += f"**{user.display_name}'s size:**\n{clit}\n"
        
        # Send the message using pagify for proper Discord formatting
        for page in pagify(msg):
            await ctx.send(page)
