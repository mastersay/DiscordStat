from datetime import datetime
from discord import Embed, Message
from discord.errors import NotFound
from discord.ext.commands import Bot, Cog
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash, cog_subcommand
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component, \
    ComponentContext, create_select, create_select_option
from main import guild_ids, trash_reaction
from mongo_db import get_collection, database


class Embeds:
    @staticmethod
    def counters(title="", description="Your counters and values", color=0x24A6DA):
        return Embed(title=title, description=description, color=color)

    @staticmethod
    def create_counter(title="New Counter", description="Add this expression counter?"):
        return Embed(title=title, description=description)

    @staticmethod
    def create_counter_successfull(title="Counter Successfully Created",
                                   description="Now you can see how many counted expressions you and your comrades "
                                               "texted", color=0x43BF6C):
        return Embed(title=title, description=description, color=color)

    @staticmethod
    def reset_counter_successfull(title="", description="Counter reset successful", color=0x43BF6C):
        return Embed(title=title, description=description, color=color)

    @staticmethod
    def delete_counter_successfull(title="", description="Counter delete successful", color=0x43BF6C):
        return Embed(title=title, description=description, color=color)

    @staticmethod
    def update_counter_name(title: str, description="Write new name of your counter"):
        return Embed(title=title, description=description)

    @staticmethod
    def update_counter_name_successfull(title="", description="Counter update successful", color=0x43BF6C):
        return Embed(title=title, description=description, color=color)

    @staticmethod
    def update_counter_expressions(title, description="Write new expressions to count separated with '; '"):
        return Embed(title=title, description=description)

    @staticmethod
    def error(description: str, title="Error occurred", color=0xC03437):
        return Embed(title=title, description=description, color=color)


def defecate_counter(lst: list[str]) -> list[str]:
    lst = sorted(set(ele.strip() for ele in lst), key=len)
    return [expression for expression in lst if
            not any(sub_exp in expression for sub_exp in lst if sub_exp != expression)]


# TODO: Secure running more instances of one command
# TODO: Texts correction
class ExpressionsCounters(Cog):
    def __init__(self, client: Bot):
        self.bot = client

    @cog_slash(name='counters', description="Shows counters and their values.", guild_ids=guild_ids)
    async def _counters(self, ctx: SlashContext):
        counters_collection = await get_collection(database, "Expressions counter")
        counters_embed = Embeds.counters()
        async for expression_counter in counters_collection.find({}):
            counters_embed.add_field(name=expression_counter['Counter_name'], value=expression_counter['Value'])
        if ctx.responded:
            counters_message = await ctx.channel.send(embed=counters_embed)
        else:
            counters_message = await ctx.send(embed=counters_embed)
        await counters_message.add_reaction(trash_reaction)

    @cog_subcommand(base="counter", name="create", description="Creates a new expression counter", guild_ids=guild_ids,
                    options=[{'name': "group_name", 'description': "Name of your counter", 'type': 3, 'required': True},
                             {'name': "expressions",
                              'description': "Enter expressions separated with '; '", 'type': 3,
                              'required': True}])
    async def _counter_create(self, ctx: SlashContext, group_name: str, expressions: str):
        counters_collection = await get_collection(database, "Expressions counter")
        if await counters_collection.find_one({'Counter_name': group_name}) is not None:
            create_counter_message = await ctx.send(
                embed=Embeds.error("Expression counter with this name already exists"))
            await create_counter_message.add_reaction(trash_reaction)
            return
        expressions_to_count: list[str] = defecate_counter(expressions.split('; '))
        counter_create_buttons = create_actionrow(
            *[create_button(style=ButtonStyle.green, label="Confirm", custom_id="True"),
              create_button(style=ButtonStyle.red, label="Deny", custom_id="False")])
        create_counter_buttons_message = await ctx.send(
            embed=Embeds.create_counter().add_field(name=group_name, value="; ".join(expressions_to_count)),
            components=[counter_create_buttons])
        answer: ComponentContext = await wait_for_component(self.bot, components=counter_create_buttons,
                                                            check=lambda response: response.author == ctx.author)
        if answer.custom_id == "True":
            await counters_collection.insert_one(
                {'Counter_name': group_name, 'Expressions to count': expressions_to_count, 'Value': 0,
                 'Since DateTime': datetime.now()})
            create_counter_message = await ctx.channel.send(
                embed=Embeds.create_counter_successfull().add_field(name=group_name,
                                                                    value="; ".join(expressions_to_count)))
        else:
            create_counter_message = await ctx.channel.send(embed=Embeds.error("Creation denied"))
        await create_counter_buttons_message.delete()
        await create_counter_message.add_reaction(trash_reaction)

    # TODO: rework to reset_many
    @cog_subcommand(base="counter", name="reset", guild_ids=guild_ids, description="Reset an expressions counter",
                    options=[
                        {'name': "group_name ", 'description': "Name of your counter", 'type': 3, 'required': False}])
    async def _counter_reset(self, ctx: SlashContext, group_name: str = None):
        async def reset_successful():
            reset_counter_successful = await ctx.channel.send(embed=Embeds.reset_counter_successfull())
            await reset_counter_successful.add_reaction(trash_reaction)
            await self._counters.invoke(ctx)

        counters_collection = await get_collection(database, "Expressions counter")
        if group_name is not None:
            if await counters_collection.find_one({'Counter_name': group_name}) is not None:
                await counters_collection.update_many({'Counter_name': group_name},
                                                      {'$set': {'Value': 0, 'Since DateTime': datetime.now()}})
                await reset_successful()
                return
            else:
                not_found_message = await ctx.send(
                    embed=Embeds.error(title="Counter not found", description="Try to pick from list below"))
                await not_found_message.add_reaction(trash_reaction)
        counter_reset_action_row = create_actionrow(
            create_select(
                options=[
                    create_select_option(expression_counter['Counter_name'], value=expression_counter['Counter_name'])
                    async for expression_counter in counters_collection.find()], placeholder="Expression counters",
                min_values=1, max_values=1))
        reset_counter_message = await ctx.send("Pick your counter to reset", components=[counter_reset_action_row])
        await reset_counter_message.add_reaction(trash_reaction)
        answer: ComponentContext = await wait_for_component(self.bot, components=counter_reset_action_row,
                                                            check=lambda response: response.author == ctx.author)
        await reset_counter_message.delete()
        await counters_collection.update_many({'Counter_name': answer.values[0]},
                                              {'$set': {'Value': 0, 'Since DateTime': datetime.now()}})
        try:
            # noinspection PyUnboundLocalVariable
            await not_found_message.delete()
        except (NotFound, UnboundLocalError):
            pass
        await reset_successful()

    # TODO: rework to delete_many
    @cog_subcommand(base="counter", name="delete", guild_ids=guild_ids,
                    description="Delete an expressions counter",
                    options=[
                        {'name': "group_name", 'description': "Name of your counter", 'type': 3, 'required': False}])
    async def _counter_delete(self, ctx: SlashContext, group_name: str = None):
        async def delete_successful():
            delete_counter_successful = await ctx.channel.send(embed=Embeds.delete_counter_successfull())
            await delete_counter_successful.add_reaction(trash_reaction)
            await self._counters.invoke(ctx)

        counters_collection = await get_collection(database, "Expressions counter")
        if group_name is not None:
            if await counters_collection.find_one({'Counter_name': group_name}) is not None:
                await counters_collection.delete_many({'Counter_name': group_name})
                await delete_successful()
                return
            else:
                not_found_message = await ctx.send(
                    embed=Embeds.error(title="Counter not found", description="Try to pick from list below"))
                await not_found_message.add_reaction(trash_reaction)
        counter_delete_action_row = create_actionrow(
            create_select(
                options=[
                    create_select_option(expression_counter['Counter_name'], value=expression_counter['Counter_name'])
                    async for expression_counter in counters_collection.find()], placeholder="Expression counters",
                min_values=1, max_values=1))
        delete_counter_message = await ctx.send("Pick your counter to delete", components=[counter_delete_action_row])
        await delete_counter_message.add_reaction(trash_reaction)
        answer: ComponentContext = await wait_for_component(self.bot, components=counter_delete_action_row,
                                                            check=lambda response: response.author == ctx.author)
        await delete_counter_message.delete()
        await counters_collection.delete_many({'Counter_name': answer.values[0]})
        try:
            # noinspection PyUnboundLocalVariable
            await not_found_message.delete()
        except (NotFound, UnboundLocalError):
            pass
        await delete_successful()

    # TODO: update counter name to optional parameter on new name
    @cog_subcommand(base="counter", name="counter_name", subcommand_group="update", guild_ids=guild_ids,
                    description="Rename you counter name",
                    options=[
                        {'name': "group_name", 'description': "Name of your counter", 'type': 3, 'required': False}])
    async def _counter_update_counter_name(self, ctx: SlashContext, group_name: str = None):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        async def update_successfull():
            update_counter_successfull = await ctx.channel.send(embed=Embeds.update_counter_name_successfull())
            await update_counter_successfull.add_reaction(trash_reaction)
            await self._counters.invoke(ctx)

        counters_collection = await get_collection(database, "Expressions counter")
        if group_name is not None:
            if await counters_collection.find_one({'Counter_name': group_name}) is not None:
                update_counter_name_message = await ctx.send(
                    embed=Embeds.update_counter_name(title=f"Counter: {group_name}"))
                await update_counter_name_message.add_reaction(trash_reaction)
                new_counter_name: Message = await self.bot.wait_for('message', check=check)
                try:
                    await update_counter_name_message.delete()
                except NotFound:
                    return
                await new_counter_name.delete()
                if await counters_collection.find_one({'Counter_name': new_counter_name.content}) is not None:
                    update_counter_name_message = await ctx.channel.send(
                        embed=Embeds.error("Expression counter with this name already exists"))
                    await update_counter_name_message.add_reaction(trash_reaction)
                    return
                counter_update_name_buttons = create_actionrow(
                    *[create_button(style=ButtonStyle.green, label="Rename", custom_id="True"),
                      create_button(style=ButtonStyle.red, label="Cancel", custom_id="False")])
                update_counter_name_buttons_message = await ctx.send(
                    embed=Embeds.update_counter_name(title="Rename counter",
                                                     description=f"Do you wish to rename **{group_name}**"
                                                                 f" to -> **{new_counter_name.content}** ?"),
                    components=[counter_update_name_buttons])
                answer: ComponentContext = await wait_for_component(self.bot, components=counter_update_name_buttons,
                                                                    check=lambda
                                                                        response: response.author == ctx.author)
                if answer.custom_id == "True":
                    await counters_collection.update_one({'Counter_name': group_name},
                                                         {'$set': {'Counter_name': new_counter_name.content}})
                    await update_successfull()
                else:
                    update_counter_name_message = await ctx.channel.send(embed=Embeds.error("Rename canceled"))
                    await update_counter_name_message.add_reaction(trash_reaction)
                await update_counter_name_buttons_message.delete()
                return
            else:
                not_found_message = await ctx.send(
                    embed=Embeds.error(title="Counter not found", description="Try to pick one from list below"))
                await not_found_message.add_reaction(trash_reaction)
        counter_update_name_action_row = create_actionrow(
            create_select(options=[
                create_select_option(expression_counter['Counter_name'], value=expression_counter['Counter_name'])
                async for expression_counter in counters_collection.find()], placeholder="Expression counters",
                min_values=1, max_values=1))
        update_counter_name_message = await ctx.send("Pick your counter to update",
                                                     components=[counter_update_name_action_row])
        await update_counter_name_message.add_reaction(trash_reaction)
        answer_group_name: ComponentContext = await wait_for_component(self.bot,
                                                                       components=counter_update_name_action_row,
                                                                       check=lambda
                                                                           response: response.author == ctx.author)
        try:
            # noinspection PyUnboundLocalVariable
            await not_found_message.delete()
        except (NotFound, UnboundLocalError):
            pass
        await update_counter_name_message.delete()
        update_counter_name_message = await ctx.send(
            embed=Embeds.update_counter_name(title=f"Counter: {answer_group_name.values[0]}"))
        await update_counter_name_message.add_reaction(trash_reaction)
        new_counter_name: Message = await self.bot.wait_for('message', check=check)
        try:
            await update_counter_name_message.delete()
        except NotFound:
            return
        await new_counter_name.delete()
        if await counters_collection.find_one({'Counter_name': new_counter_name.content}) is not None:
            update_counter_name_message = await ctx.channel.send(
                embed=Embeds.error("Expression counter with this name already exists"))
            await update_counter_name_message.add_reaction(trash_reaction)
            return
        counter_update_name_buttons = create_actionrow(
            *[create_button(style=ButtonStyle.green, label="Rename", custom_id="True"),
              create_button(style=ButtonStyle.red, label="Cancel", custom_id="False")])
        update_counter_name_buttons_message = await ctx.send(
            embed=Embeds.update_counter_name(title="Rename counter",
                                             description=f"Do you wish to rename **{answer_group_name.values[0]}**"
                                                         f" to -> **{new_counter_name.content}** ?"),
            components=[counter_update_name_buttons])
        answer: ComponentContext = await wait_for_component(self.bot, components=counter_update_name_buttons,
                                                            check=lambda
                                                                response: response.author == ctx.author)
        if answer.custom_id == "True":
            await counters_collection.update_one({'Counter_name': answer_group_name.values[0]},
                                                 {'$set': {'Counter_name': new_counter_name.content}})
            await update_successfull()
        else:
            update_counter_name_message = await ctx.channel.send(embed=Embeds.error("Rename canceled"))
            await update_counter_name_message.add_reaction(trash_reaction)
        await update_counter_name_buttons_message.delete()

    # TODO: update counter name to optional parameter on new name
    @cog_subcommand(base="counter", name="expressions_to_count", subcommand_group="update", guild_ids=guild_ids,
                    description="Change you expressions to count",
                    options=[
                        {'name': "group_name", 'description': "Name of your counter", 'type': 3, 'required': False}])
    async def _counter_update_expressions_to_count(self, ctx: SlashContext, group_name: str = None):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        async def update_successfull():
            update_counter_successfull = await ctx.channel.send(embed=Embeds.update_counter_name_successfull())
            await update_counter_successfull.add_reaction(trash_reaction)
            await self._counters.invoke(ctx)

        counters_collection = await get_collection(database, "Expressions counter")
        if group_name is not None:
            counter_from_group_name: dict = await counters_collection.find_one({'Counter_name': group_name})
            if counter_from_group_name is not None:
                update_counter_expressions_message = await ctx.send(
                    embed=Embeds.update_counter_expressions(title=f"Counter: {group_name}"))
                await update_counter_expressions_message.add_reaction(trash_reaction)
                new_counter_name: Message = await self.bot.wait_for('message', check=check)
                try:
                    await update_counter_expressions_message.delete()
                except NotFound:
                    return
                await new_counter_name.delete()
                new_expressions_to_count = defecate_counter(new_counter_name.content.split('; '))
                counter_update_expressions_buttons = create_actionrow(
                    *[create_button(style=ButtonStyle.green, label="Change", custom_id="True"),
                      create_button(style=ButtonStyle.red, label="Cancel", custom_id="False")])
                update_counter_expressions_buttons_message = await ctx.send(
                    embed=Embeds.update_counter_expressions(title="Change expressions",
                                                            description="Do you wish to change **{0}** to -> **{1}** ?"
                                                            .format(counter_from_group_name.get('Expressions to count'),
                                                                    new_expressions_to_count)),
                    components=[counter_update_expressions_buttons])
                answer: ComponentContext = await wait_for_component(self.bot,
                                                                    components=counter_update_expressions_buttons,
                                                                    check=lambda
                                                                        response: response.author == ctx.author)
                if answer.custom_id == "True":
                    await counters_collection.update_one({'Counter_name': group_name},
                                                         {'$set': {'Expressions to count': new_expressions_to_count}})
                    await update_successfull()
                else:
                    update_counter_expressions_message = await ctx.channel.send(embed=Embeds.error("Change canceled"))
                    await update_counter_expressions_message.add_reaction(trash_reaction)
                await update_counter_expressions_buttons_message.delete()
                return
            else:
                not_found_message = await ctx.send(
                    embed=Embeds.error(title="Counter not found", description="Try to pick one from list below"))
                await not_found_message.add_reaction(trash_reaction)
        counter_update_expressions_action_row = create_actionrow(
            create_select(options=[
                create_select_option(expression_counter['Counter_name'], value=expression_counter['Counter_name'])
                async for expression_counter in counters_collection.find()], placeholder="Expression counters",
                min_values=1, max_values=1))
        update_counter_expressions_message = await ctx.send("Pick your counter to update",
                                                            components=[counter_update_expressions_action_row])
        await update_counter_expressions_message.add_reaction(trash_reaction)
        answer_group_name: ComponentContext = await wait_for_component(self.bot,
                                                                       components=counter_update_expressions_action_row,
                                                                       check=lambda
                                                                           response: response.author == ctx.author)
        try:
            # noinspection PyUnboundLocalVariable
            await not_found_message.delete()
        except (NotFound, UnboundLocalError):
            pass
        await update_counter_expressions_message.delete()
        update_counter_expressions_message = await ctx.send(
            embed=Embeds.update_counter_expressions(title=f"Counter: {answer_group_name.values[0]}"))
        await update_counter_expressions_message.add_reaction(trash_reaction)
        new_counter_name: Message = await self.bot.wait_for('message', check=check)
        try:
            await update_counter_expressions_message.delete()
        except NotFound:
            return
        await new_counter_name.delete()
        new_expressions_to_count = defecate_counter(new_counter_name.content.split('; '))
        counter_from_group_name = await counters_collection.find_one({'Counter_name': answer_group_name.values[0]})
        counter_update_expressions_buttons = create_actionrow(
            *[create_button(style=ButtonStyle.green, label="Rename", custom_id="True"),
              create_button(style=ButtonStyle.red, label="Cancel", custom_id="False")])
        update_counter_expressions_buttons_message = await ctx.send(
            embed=Embeds.update_counter_expressions(title="Change expressions",
                                                    description="Do you wish to change **{0}** to -> **{1}** ?"
                                                    .format(counter_from_group_name.get('Expressions to count'),
                                                            new_expressions_to_count)),
            components=[counter_update_expressions_buttons])
        answer: ComponentContext = await wait_for_component(self.bot, components=counter_update_expressions_buttons,
                                                            check=lambda
                                                                response: response.author == ctx.author)
        if answer.custom_id == "True":
            await counters_collection.update_one({'Counter_name': answer_group_name.values[0]},
                                                 {'$set': {'Expressions to count': new_expressions_to_count}})
            await update_successfull()
        else:
            update_counter_expressions_message = await ctx.channel.send(embed=Embeds.error("Rename canceled"))
            await update_counter_expressions_message.add_reaction(trash_reaction)
        await update_counter_expressions_buttons_message.delete()


def setup(client: Bot):
    client.add_cog(ExpressionsCounters(client))
