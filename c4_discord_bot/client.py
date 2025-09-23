import discord
from discord.ext import commands
from os import environ
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from functools import partial

from c4_discord_bot.updater import do_auto_update


class Client(commands.Bot):
    scheduler = AsyncIOScheduler()

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def setup_hook(self):
        await self.load_scheduler()
        await self.load_cogs()
        await self.sync_tree()

    async def sync_tree(self):
        # must be in development mode to sync locally
        if environ.get("ENV") == "development":
            if environ.get("TEST_GUILD_ID") is None:
                print(
                    "TEST_GUILD_ID not set! Can't do fast sync. Falling back to globally syncing..."
                )
                await self.tree.sync()
            TEST_GUILD = discord.Object(id=environ.get("TEST_GUILD_ID"))
            self.tree.copy_global_to(guild=TEST_GUILD)
            await self.tree.sync(guild=TEST_GUILD)
        else:
            await self.tree.sync()

    async def load_cogs(self):
        if environ.get("ENV") == "development":
            await self.load_extension("c4_discord_bot.cogs.development")
        await self.load_extension("c4_discord_bot.cogs.neofetch")
        await self.load_extension("c4_discord_bot.cogs.washing_machine")
        await self.load_extension("c4_discord_bot.cogs.admin_bulk_events")
    
    async def load_scheduler(self):
        if environ.get("ENV") == "production" and not bool(environ.get("DISABLE_AUTO_UPDATE", False)):
            self.scheduler.add_job(
                do_auto_update, 'cron', args=(self,), hour='0', minute='10', second='0', jitter=120
            )
        self.scheduler.start()


intents = discord.Intents.all()
client = Client(
    "!!!", intents=intents
)  # !!! is our prefix. since we're using slash commands, this is not used. it's still needed, though.
