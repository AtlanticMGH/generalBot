import discord
from discord.ext import commands
from discord import option
from helper.sql_helper import Sql_helper
from helper.modLogs import ModLogs
from helper.warn_helper import Warn_helper
import time
from datetime import timedelta

class AdminBasis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.modLogs = ModLogs()
        self.sql_helper = Sql_helper()
        self.warn_helper = Warn_helper()

    @discord.slash_command(
        name="help",
        description="Zeigt das Hilfe-Menü der Basisversion an",
        default_member_permissions=discord.Permissions(administrator=True)
    )
    async def help(self, ctx):
        try:
            help_embed = discord.Embed(title="Help",
                            colour=0x14ec1a)

            help_embed = discord.Embed(
                title="🤖 Bot Hilfe-Menü",
                description="Hier ist eine Übersicht aller verfügbaren Funktionen und Befehle der aktuellen Basisversion.",
                color=discord.Color.blurple()
            )
            # Basis-Funktion (Wortfilter)
            help_embed.add_field(
                name="🛡️ Auto-Moderation (Passiv)",
                value="Der Bot überwacht den Chat automatisch. Nachrichten, die auf der Blacklist stehende Wörter enthalten, werden **sofort gelöscht**, um den Chat sauber zu halten.",
                inline=False
            )

            help_embed.add_field(
                name="🥾 /kick <@user> [grund]",
                value="Entfernt ein Mitglied vom Server. Die Person kann über einen Einladungslink jederzeit wieder beitreten.",
                inline=False
            )
            help_embed.add_field(
                name="🔨 /ban <@user> [grund]",
                value="Bannt ein Mitglied permanent vom Server, sodass es nicht mehr beitreten kann.",
                inline=False
            )
            # Nützliche Utility-Befehle
            help_embed.add_field(
                name="🏓 /ping",
                value="Prüft, ob der Bot online ist und zeigt die aktuelle Latenz in Millisekunden an.",
                inline=True
            )
            help_embed.add_field(
                name="ℹ️ /userinfo <@user>",
                value="Zeigt Account-Details eines Nutzers (z.B. Erstellungsdatum, Server-Beitritt, höchste Rolle).",
                inline=True
            )
            # Optionaler Footer für einen sauberen Abschluss
            help_embed.set_footer(text="Parameter in <> sind Pflicht, Parameter in [] sind optional.")

            await ctx.respond(embed=help_embed, ephemeral=True)
        except Exception as e:
            print(f"Fehler aufgetreten: {e}")

    @discord.slash_command(name="kick", description="Kickt einen User", default_member_permissions=discord.Permissions(administrator=True))
    @option("member", discord.Member, required=True)
    @option("grund", str, required=False, default="")
    async def kick(self, ctx, member: discord.Member, grund):
        try:
            await member.kick(reason=grund)
            self.modLogs.log_hinzufuegen(ctx.guild.id, member.id, f"Gekickt von: {ctx.author.name} \n Grund: {grund}", "kick", time.strftime('%Y-%m-%d %H:%M:%S'))
            if grund:
                await ctx.respond(f"`{member.name}` wurde wegen `{grund}` gekickt", ephemeral=True)
            else:
                await ctx.respond(f"`{member.name}` wurde gekickt", ephemeral=True)
        except Exception as e:
            print(f"Fehler beim kicken: \n {e}")
            await ctx.respond(f"Fehler beim kicken von `{member.name}`", ephemeral=True)

    @discord.slash_command(name="ban", description="Bannt einen User", default_member_permissions=discord.Permissions(administrator=True))
    @option("member", discord.Member, required=True)
    @option("grund", str, required=False, default="")
    async def ban(self, ctx, member: discord.Member, grund):
        try:
            await member.ban(reason=grund)
            self.modLogs.log_hinzufuegen(ctx.guild.id, member.id,  f"Gebannt von: {ctx.author.name} \n Grund: {grund}", "ban", time.strftime('%Y-%m-%d %H:%M:%S'))
            if grund:
                await ctx.respond(f"`{member.name}` wurde wegen `{grund}` gebannt", ephemeral=True)
            else:
                await ctx.respond(f"`{member.name}` wurde gebannt", ephemeral=True)
        except Exception as e:
            print(f"Fehler beim bannen: \n{e}")
            await ctx.respond(f"Fehler beim bannen von `{member.name}`", ephemeral=True)

    # Befehle für Auto-Mod
    @discord.slash_command(
        name="add_banned_word",
        description="Fügt ein Wort zur Auto-Mod Blacklist hinzu",
        default_member_permissions=discord.Permissions(administrator=True)
    )
    @option("word", str, required=True, default="")
    async def add_banned_word(self, ctx, word):
        try:
            self.sql_helper.add_banned_word(word.lower(), str(ctx.guild.id))
            await ctx.respond(f"{word} erfolgreich geblacklistet", ephemeral=True)
        except Exception as e:
            print(f"Fehler beim wort blacklisten: \n {e}")
            await ctx.respond(f"Beim blacklisten von {word} ist ein Fehler aufgetreten!", ephemeral=True)

    @discord.slash_command(
        name="remove_banned_word",
        description="Entfernt ein Wort von der Auto-Mod Blacklist",
        default_member_permissions=discord.Permissions(administrator=True)
    )
    @option("word", str, required=True, default="")
    async def remove_banned_word(self, ctx, word):
        try:
            self.sql_helper.delete_banned_word(word.lower(), str(ctx.guild.id))
            await ctx.respond(f"{word} erfolgreich von der Blacklist enfernt", ephemeral=True)
        except Exception as e:
            print(f"Fehler beim wort entblacklisten: \n {e}")
            await ctx.respond(f"Beim entfernen von {word} ist ein Fehler aufgetreten!", ephemeral=True)

    @discord.slash_command(
        name="read_banned_words",
        description="Liest die Auto-Mod Blacklist",
        default_member_permissions=discord.Permissions(administrator=True)
    )
    async def show_banned_words(self, ctx):
        try:
            words = self.sql_helper.read_banned_words(str(ctx.guild.id))

            embed = discord.Embed(title="Gebannte Wörter",colour=0xe01b24)

            for i in range(len(words)):
                embed.add_field(name=i+1, value=words[i], inline=False)

            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Fehler beim lesen von gebannten wörtern: \n {e}")
            await ctx.respond(f"Fehler beim lesen von gebannten wörtern!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        try:
            blacklist = self.sql_helper.read_banned_words(str(message.guild.id))
            message_lower = message.content.lower()

            for banned_word in blacklist:
                if banned_word.lower() in message_lower:
                    await message.delete()
                    self.warn_helper.add_warn(message.author.id, message.guild.id)
                    warns = self.warn_helper.read_warns(message.author.id, message.guild.id)
                    if warns[0] >= 3:
                        await message.author.timeout_for(timedelta(hours=6))
                        self.warn_helper.reset_warns(message.guild.id, message.author.id)
                    # Evtl einbauen, kann nervig sein
                    #try:
                    #    await message.author.send(f"Deine Nachricht auf **{message.guild.name}** wurde gelöscht, weil sie das Word **{banned_word}** enthielt.")
                    #except discord.Forbidden:
                    #    pass
                    return
        except Exception as e:
            print(f"Auto-Mod Fehlfunktion: {e}!")

def setup(bot):
    bot.add_cog(AdminBasis(bot))
