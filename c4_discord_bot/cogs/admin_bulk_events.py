from discord.ext.commands import Cog, Bot
from discord import Interaction, Embed, app_commands, Attachment, EntityType, PrivacyLevel
import icalendar

class BulkEventCreator(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(create_events=True)
    @app_commands.describe(events="A .ics file containing all of the events to create")
    async def bulk_create_events(self, interaction: Interaction, events: Attachment):
        if events.content_type not in ["text/calendar; charset=utf-8"]:
            await interaction.response.send_message(f"What's in here? {events.content_type}", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)

        # alright, read the ics file, get all the events in the file, and then make a discord event. simple, really.

        try:
            ics_content = await events.read()
            ics_text = ics_content.decode('utf-8')
            # parse :>
            calendar = icalendar.Calendar.from_ical(ics_text)

        except Exception as e:
            await interaction.followup.send(f"Failed to read the file: {str(e)}", ephemeral=True)
            return
        
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
            return

        for event in calendar.events:
            await guild.create_scheduled_event(
                name=str(event.get('summary')).strip(),
                start_time=event.get('dtstart').dt,
                end_time=event.get('dtend').dt,
                description=str(event.get('description')).strip(),
                entity_type=EntityType.external,
                privacy_level=PrivacyLevel.guild_only,
                location=str(event.get('location')).strip() if event.get('location') else "To Be Determined!",
                reason=f"Bulk event creation via .ics file ({interaction.user})",
            )

        await interaction.followup.send(f"Created {len(calendar.events)} events!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BulkEventCreator(bot))
