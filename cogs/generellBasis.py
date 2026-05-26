import discord
from discord.ext import commands
from discord.utils import format_dt
from discord import option

class GenerellBasis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="userinfo",
        description="Zeigt Informationen über einen Nutzer an."
    )
    @option(
        "member",
        discord.Member,
        required=False,
        default=None
    )
    async def userinfo(self, ctx, member: discord.Member):
        # Wenn kein User angegeben wurde, nimm den Ausführenden selbst
        member = member or ctx.author

        # Höchste Rolle ermitteln (ohne @everyone)
        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        highest_role = member.top_role.mention if len(roles) > 0 else "Keine"
        # Embed erstellen
        user_embed = discord.Embed(
            title=f"User Info: {member.name}",
            color=member.color
        )
        user_embed.set_thumbnail(url=member.display_avatar.url)
        # Felder hinzufügen
        user_embed.add_field(name="Name", value=member.name, inline=True)
        user_embed.add_field(name="ID", value=str(member.id), inline=True)
        joined_at_string = format_dt(member.joined_at, style="d") if member.joined_at else "Unbekannt"
        created_at_string = format_dt(member.created_at, style="d") if member.created_at else "Unbekannt"
        user_embed.add_field(
            name="Server beigetreten",
            value=joined_at_string,
            inline=True
        )
        user_embed.add_field(
            name="Account erstellt",
            value=created_at_string,
            inline=True
        )
        user_embed.add_field(name="Höchste Rolle", value=highest_role, inline=False)
        user_embed.add_field(
            name="Rollen",
            value=", ".join(roles) if roles else "Keine",
            inline=False
        )
        await ctx.respond(embed=user_embed, ephemeral=True)




def setup(bot):
    bot.add_cog(GenerellBasis(bot))