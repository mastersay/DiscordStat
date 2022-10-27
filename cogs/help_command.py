from discord import Embed
from discord.ext.commands import Bot, Cog
from discord_slash.cog_ext import cog_slash
from discord_slash import SlashContext
from main import guild_ids, trash_reaction


# TODO: Texts correction
class Help(Cog):
    HELP_EMBED = Embed.from_dict(  # TODO: missing parameters description
        {'title': "Commands in DiscordStat bot", 'color': 0xFFFFFF,
         'fields': [{'name': "```/counters```", 'value': "Shows expression counters and their values"},
                    {'name': "```/counter create```",
                     'value': "Creates a new expression counter\n**Parameters:**"
                              "\n`group_name`: Name of your new expression counter"
                              "\n`description`: Enter expressions separated with '; '"},
                    {'name': "```/counter reset```",
                     'value': "Resets an expressions counter\n**Parameters**:"
                              "\n**[optional]** `group_name`: Name of your expressions counter, if not filled,"
                              " list of counters will shows for you to pick"},
                    {'name': "```/counter delete```",
                     'value': "Deletes an expressions counter\n**Parameters**:"
                              "\n**[optional]** `group_name`: Name of your expressions counter, if not filled,"
                              " list of counters will shows for you to pick"},
                    {'name': "```/counter update counter_name```",
                     'value': "Updates a name of you expression counter\n**Parameters**:"
                              "\n**[optional]** `group_name`: Name of your expressions counter, if not filled,"
                              " list of counters will shows for you to pick"},
                    {'name': "```/counter update expressions_to_count```",
                     'value': "Updates an expressions in you counter\n**Parameters**:"
                              "\n**[optional]** `group_name`: Name of your expressions counter, if not filled,"
                              " list of counters will shows for you to pick"},
                    {'name': "```/activity channels```",
                     'value': "Shows recorded channel activity: room time, messages\n**Parameters**:"
                              "\n`channel`: Channel to show activity for, choose just specific channel, not groups"
                              "\n**[optional]** `user`: Activity in chosen channel for specific user"},
                    {'name': "```/activity users```",
                     'value': "Shows recorded user activity: room time, messages\n**Parameters**:"
                              "\n`user`: Activity for picked user"
                              "\n**[optional]** `channel`: Activity for chosen user in specific channel, "
                              "choose just specific channel, not groups"},
                    {'name': "```/activity total```",
                     'value': "Shows recorded guild activity: room time, room call, messages"},
                    {'name': "**Warnings**",
                     'value': "\n> Wrong usage of 'semicolon space'"
                              " separator will lead to wrong recognition of expressions"
                              "\n> It isn't possible to have 2 counters with the same name"
                              "\n> Activities aren't recorded for bot members"}]})

    def __init__(self, client: Bot):
        self.bot = client

    @cog_slash(name='help', description="Commands that can be used", guild_ids=guild_ids)
    async def _help(self, ctx: SlashContext):
        help_message = await ctx.send(embed=self.HELP_EMBED)
        await help_message.add_reaction(trash_reaction)


def setup(client: Bot):
    client.add_cog(Help(client))
