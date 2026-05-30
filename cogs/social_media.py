import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import json
import re
import asyncio
import logging
from typing import Optional, Dict
import time
import urllib.parse
from googleapiclient.discovery import build
import instaloader
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger('discord')

class SocialMedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.last_request_time = 0
        self.rate_limit_delay = 2  # Seconds between requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Load YouTube API key from .env
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.youtube_api_key:
            raise ValueError("YouTube API key not found in .env file. Please set YOUTUBE_API_KEY.")
        self.youtube_service = build('youtube', 'v3', developerKey=self.youtube_api_key, cache_discovery=False)

    async def cog_load(self):
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    @app_commands.command()
    @app_commands.describe(url="The Instagram post/reel URL to download and repost")
    async def instagram_repost(self, interaction: discord.Interaction, url: str):
        """Downloads and reposts an Instagram post or reel"""
        # Send immediate response to avoid timeout
        await interaction.response.send_message("[Downloading] Getting Instagram content, please wait...", ephemeral=False)

        try:
            if 'instagram.com' not in url:
                await interaction.edit_original_response(content="[ERROR] Please provide a valid Instagram URL")
                return

            # Extract shortcode from URL
            shortcode = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
            
            # Download Instagram content in background thread
            def download_instagram(shortcode):
                import tempfile
                import os
                import shutil
                
                # Create temp directory for downloads
                temp_dir = tempfile.mkdtemp()
                try:
                    L = instaloader.Instaloader(dirname_pattern=temp_dir, filename_pattern="{shortcode}")
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    L.download_post(post, target=temp_dir)
                    
                    # Find downloaded files
                    files = []
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        if file.endswith(('.mp4', '.jpg', '.png')):
                            files.append(file_path)
                    
                    return files, temp_dir, None
                except Exception as e:
                    return [], temp_dir, str(e)

            files, temp_dir, error = await asyncio.to_thread(download_instagram, shortcode)
            
            if error:
                await interaction.edit_original_response(content=f"[ERROR] Error downloading: {error}")
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            if not files:
                await interaction.edit_original_response(content="[ERROR] No media files found in this Instagram post")
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            # Send the first video/image file
            import os
            primary_file = files[0]
            file_size = os.path.getsize(primary_file) / (1024 * 1024)  # MB
            
            if file_size > 25:  # Discord's 25MB limit for regular uploads
                await interaction.edit_original_response(content=f"[ERROR] File is too large to upload ({file_size:.1f}MB). Discord limit is 25MB.")
            else:
                await interaction.edit_original_response(content=f"[SUCCESS] Downloaded from Instagram!\n{url}")
                await interaction.followup.send(file=discord.File(primary_file))
            
            # Cleanup temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            logger.error(f"Instagram repost error: {str(e)}", exc_info=True)
            try:
                await interaction.edit_original_response(content=f"[ERROR] An error occurred: {str(e)}")
            except:
                pass

async def setup(bot):
    await bot.add_cog(SocialMedia(bot))