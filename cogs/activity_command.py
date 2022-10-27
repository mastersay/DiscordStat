from discord.ext.commands import Bot, Cog
from discord import Embed, RawReactionActionEvent, Message, Member
from discord_slash.cog_ext import cog_slash, cog_subcommand
from discord_slash import SlashContext
from main import guild_ids, trash_reaction
from mongo_db import get_collection, database


class Activity(Cog):

    def __init__(self, client: Bot):
        self.bot = client

    # TODO: Activity command
    # @cog_slash(name="activity", description="Shows recorded guild, channel or user activity", guild_ids=guild_ids,
    #            options=[
    #                {'name': "activity_type", 'description': "Shows guild activity if user parameter is not entered",
    #                 'type': 4, 'required': True,
    #                 'choices': [{'name': "Total", 'value': 0}, {'name': "Chat activity", 'value': 1},
    #                             {'name': "Voice activity", 'value': 2},
    #                             {'name': "Guild activity", 'value': 3}]},
    #                {'name': "user", 'description': "Activity for user", 'type': 6, 'required': False}])
    # async def _activity(self, ctx: SlashContext, activity_type: str = None, user: Member = None):
    #     print(ctx, activity_type, user)
    #     await ctx.send(content="none")
    #     e = Embed(title=" t", description=" none ")
    #     for i in range(100):
    #         e.add_field(name=str(i), value=str(i))
    #         if i % 24 == 0:
    #             await ctx.channel.send(embed=e)
    #             e.clear_fields()

    @cog_subcommand(base="activity", name="channels", description="Shows recorded channel activity",
                    guild_ids=guild_ids,
                    options=[{'name': 'channel', 'description': "Pick channel to show activity for", 'type': 7,
                              'required': True},
                             {'name': 'user', 'description': "Show channel activity for this user", 'type': 6,
                              'required': False}])
    async def _activity_channels(self, ctx: SlashContext, channel, user: Member = None):
        print(type(channel), type(user))

    @cog_subcommand(base="activity", name="users", description="Shows recorded user activity", guild_ids=guild_ids,
                    options=[{'name': 'user', 'description': "Pick user to show activity for", 'type': 6,
                              'required': True},
                             {'name': 'channel', 'description': "Show user activity in this channel", 'type': 7,
                              'required': False}])
    async def _activity_users(self, ctx: SlashContext, user: Member, channel=None):
        print(user, channel)

    @cog_subcommand(base="activity", name="total", description="", guild_ids=guild_ids)
    async def _activity_total(self, ctx: SlashContext):
        pass


def setup(client: Bot):
    client.add_cog(Activity(client))
