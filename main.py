from discord import Message, RawReactionActionEvent, Embed
from discord.ext.tasks import loop
from discord.ext.commands import Bot
from discord.errors import HTTPException, NotFound
from discord_slash import SlashCommand, SlashContext
import os
# import pymongo
from mongo_db import get_collection, database

# database = None


# l = asyncio.get_event_loop()
# database = l.run_until_complete(connect_to_database('main'))
# l.close()
# print(database)
trash_reaction = "\U0001f5d1"

n = 0


class MyBot(Bot):
    def __init__(self, **kwargs):
        super(MyBot, self).__init__(command_prefix='/', **kwargs)
        self.database = None

    async def on_connect(self):
        # global database
        # self.database = await connect_to_database("main")
        print(f"Logged on as {self.user}")
        for file_name in os.listdir("cogs"):
            if file_name.endswith(".py"):
                bot.load_extension(f"cogs.{file_name[:-3]}")

    async def on_ready(self):
        print(f"Bot ready to work as {self.user}")
        self.cog_reload.start()

    # noinspection PyMethodOverriding
    @staticmethod
    async def on_message(message: Message):
        if message.author.bot:
            return
        counters_collection = await get_collection(database, "Expressions counter")
        async for counter in counters_collection.find():
            for expression_to_count in counter['Expressions to count']:
                count = message.content.count(expression_to_count)
                if count > 0:
                    await counters_collection.update_one(
                        {'Counter_name': counter['Counter_name'], 'Expressions to count': expression_to_count},
                        {'$inc': {'Value': count}})

    @staticmethod
    async def on_raw_reaction_add(payload: RawReactionActionEvent):
        if payload.emoji.name == trash_reaction:
            message: Message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if any([True for reaction in message.reactions if reaction.count > 1 and any(
                    [True for user in await reaction.users(limit=None).flatten() if user.bot])]):
                if not payload.member.bot:  # TODO: Secure for deletion for not command user
                    try:
                        await message.delete()
                    except NotFound:
                        pass

    @staticmethod
    @loop(seconds=5)
    async def cog_reload():
        for file_name in os.listdir("cogs"):
            if file_name.endswith(".py"):
                bot.reload_extension(f"cogs.{file_name[:-3]}")
        global n
        n += 1
        print("cog reloaded", n)


guild_ids = [764941750229270539]
bot = MyBot()
while True:
    try:
        slash_command = SlashCommand(bot, sync_commands=True)
    except HTTPException:
        pass
    else:
        break


def sub_test(*args):
    print(args)


# counter_sub_commands = [{'name': "create",
#                          'description': "Create a new expressions counter",
#                          'type': 1},
#                         {'name': "reset",
#                          'description': "Reset all counters or chosen counter",
#                          'type': 1},
#                         {'name': "delete",
#                          'description': "Delete selected counters",
#                          'type': 1},
#                         {'name': "update",
#                          'description': "For changing 'words to count' in counter",
#                          'type': 1}]


@slash_command.slash(name="test", description="", guild_ids=guild_ids,
                     options=[{'name': "embed", 'description': "none", 'type': 3, 'required': False}])
async def _test(ctx: SlashContext, embed=None):
    if embed is None:
        embed = {'title': "ℭ𝔬𝔪𝔪𝔞𝔫𝔡𝔰 𝔦𝔫 𝔇𝔦𝔰𝔠𝔬𝔯𝔡𝔖𝔱𝔞𝔱 𝔟𝔬𝔱", 'fields': [
            {'name': '```diff \n----------------------------------------------------```',
             'value': '**`/counters`**Shows expression counters and their values'},
            {'name': '----------------------------------------------------',
             'value': '**`/counters`**Shows expression counters and their values'}]}
    else:
        # print(eval(embed))
        embed = eval(embed)
    # await ctx.send(embed=Embed.from_dict(eval(embed)))
    await ctx.send(embed=Embed.from_dict(embed))

    # # ctx.message.add_reaction("😁")
    # select = create_select(
    #     options=[  # the options in your dropdown
    #         create_select_option("Lab Coat", value="coat", emoji="🥼"),
    #         create_select_option("Test Tube", value="tube", emoji="🧪"),
    #         create_select_option("Petri Dish", value="dish", emoji="🧫"),
    #     ],
    #     # placeholder="Choose your option",  # the placeholder text to show when no options have been chosen
    #     min_values=1,  # the minimum number of options a user must select
    #     max_values=2,  # the maximum number of options a user can select
    # )
    #
    # message = await ctx.send("test", components=[
    #     create_actionrow(select)])  # like action row with buttons but without * in front of the variable
    # await message.add_reaction("😀")
    # await message.delete(delay=2)


# TODO: implementation on database ('in progress')
if __name__ == '__main__':
    # noinspection SpellCheckingInspection
    bot.run("")
    # bot.close()
