from typing import Optional
from discord.ext.commands import Cog, Bot
from discord import Interaction, app_commands, Attachment, File, Member, AllowedMentions
from PIL import Image, ImageDraw
from io import BytesIO
import asyncio

class WashingMachine(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(image="The image to put through the spin cycle", speed="How fast to spin the image")
    @app_commands.choices(speed=[
        app_commands.Choice(name="delicate", value="delicate"),
        app_commands.Choice(name="normal", value="normal"),
        app_commands.Choice(name="heavy duty", value="heavy duty"),
        app_commands.Choice(name="super spin", value="super spin"),
        app_commands.Choice(name="ludicrous speed", value="ludicrous speed")
    ])
    async def spin_cycle(self, interaction: Interaction, image: Attachment, speed: Optional[str] = "normal", counterclockwise: Optional[bool] = False):
        """Put an image through the spin cycle"""
        if image.content_type not in ["image/png", "image/jpeg", "image/webp"]:
            await interaction.response.send_message("That's not an image!", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        # speed is how many how many times it spins
        # 1 rot = 360 degrees
        # delicate = a gentle spin (10rot:30s)
        # normal = a normal spin (50rot:60s)
        # heavy duty = a heavy spin (150rot:60s)
        # super spin = a super spin (250rot:60s)
        # ludicrous speed = LUDICROUS (500rot:60s)
        # of course, those ratios should be adjusted so the image doesnt take too long to process
        # since these are all ratios...
        fps = 25
        rot_per_frame = -1
        if speed == "delicate":
            rot_per_frame = 10 / (30 * fps)
        elif speed == "normal":
            rot_per_frame = 50 / (60 * fps)
        elif speed == "heavy duty":
            rot_per_frame = 150 / (60 * fps)
        elif speed == "super spin":
            rot_per_frame = 250 / (60 * fps)
        elif speed == "ludicrous speed":
            rot_per_frame = 500 / (60 * fps)
        degrees_per_frame = rot_per_frame * 360 * (-1 if counterclockwise else 1)

        # img = self.spin_image(image, image_to_spin=BytesIO(await image.read()), degrees_per_frame=degrees_per_frame, fps=fps)
        img = await asyncio.get_event_loop().run_in_executor(None, self.spin_image, BytesIO(await image.read()), degrees_per_frame, fps)
        file = File(img, filename="spin_cycle.webp")

        await interaction.followup.send(file=file)
    
    @app_commands.command()
    @app_commands.describe(person="The person to put through the spin cycle", speed="How fast to spin the image")
    @app_commands.choices(speed=[
        app_commands.Choice(name="delicate", value="delicate"),
        app_commands.Choice(name="normal", value="normal"),
        app_commands.Choice(name="heavy duty", value="heavy duty"),
        app_commands.Choice(name="super spin", value="super spin"),
        app_commands.Choice(name="ludicrous speed", value="ludicrous speed")
    ])
    async def spin_cycle_person(self, interaction: Interaction, person: Member, speed: Optional[str] = "normal", counterclockwise: Optional[bool] = False):
        """Put a person through the spin cycle"""
        if not person.avatar:
            await interaction.response.send_message("That person doesn't have an avatar!", ephemeral=True)
            return
         
        await interaction.response.defer(thinking=True)
        # speed is how many how many times it spins
        # 1 rot = 360 degrees
        # delicate = a gentle spin (10rot:30s)
        # normal = a normal spin (50rot:60s)
        # heavy duty = a heavy spin (150rot:60s)
        # super spin = a super spin (250rot:60s)
        # ludicrous speed = LUDICROUS (500rot:60s)
        # of course, those ratios should be adjusted so the image doesnt take too long to process
        # since these are all ratios...
        fps = 25
        rot_per_frame = -1
        if speed == "delicate":
            rot_per_frame = 10 / (30 * fps)
        elif speed == "normal":
            rot_per_frame = 50 / (60 * fps)
        elif speed == "heavy duty":
            rot_per_frame = 150 / (60 * fps)
        elif speed == "super spin":
            rot_per_frame = 250 / (60 * fps)
        elif speed == "ludicrous speed":
            rot_per_frame = 500 / (60 * fps)
        degrees_per_frame = rot_per_frame * 360 * (-1 if counterclockwise else 1)

        # img = self.spin_image(image, image_to_spin=BytesIO(await image.read()), degrees_per_frame=degrees_per_frame, fps=fps)
        img = await asyncio.get_event_loop().run_in_executor(None, self.spin_image, BytesIO(await person.avatar.read()), degrees_per_frame, fps)
        file = File(img, filename="spin_cycle.webp")

        await interaction.followup.send(f"{person.mention} has been put through the spin cycle", file=file, allowed_mentions=AllowedMentions.none())
    
    def spin_image(self, image_to_spin: BytesIO, degrees_per_frame: float, fps: int):
        image_to_spin.seek(0)
        final_image = BytesIO()

        washer_image = Image.open("c4_discord_bot/cogs/washing_machine.jpg")
        overlay_image = Image.open(image_to_spin)
        # crop overlay image to a circle
        overlay_image = overlay_image.resize((400, 400))
        overlay_image = overlay_image.convert("RGBA")
        circle = Image.new("L", overlay_image.size, 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0) + overlay_image.size, fill=round(255*.7))
        overlay_image.putalpha(circle)
        frames = []
        cur_degrees = 0
        while True:
            frame = washer_image.copy()
            overlay_image_rotated = overlay_image.rotate(cur_degrees, resample=Image.BICUBIC)
            frame.paste(overlay_image_rotated, (300, 265), overlay_image_rotated)
            frames.append(frame)
            cur_degrees -= degrees_per_frame
            # exit if we're above 10 rotations OR we're perfectly aligned
            if cur_degrees <= -3600 or cur_degrees >= 3600 or abs(cur_degrees) % 360 < 1:
                break

        frames[0].save(final_image, format="webp", save_all=True, append_images=frames[1:], duration=1000/fps, loop=0)
        final_image.seek(0)
        return final_image


async def setup(bot):
    await bot.add_cog(WashingMachine(bot))
