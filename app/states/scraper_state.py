import reflex as rx
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import time
from typing import TypedDict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Channel(TypedDict):
    id: str
    name: str
    logo: str
    stream_path: str
    tags: str
    m3u8_url: str
    status: str
    last_updated: float


class ScraperState(rx.State):
    channels: list[Channel] = []
    is_scanning: bool = False
    scan_progress: int = 0
    total_channels: int = 0
    logs: list[str] = []
    last_full_scan: float = 0.0
    scan_status_message: str = "Ready to scan"
    auto_refresh: bool = False
    search_query: str = ""
    selected_tag: str = "All"

    @rx.var
    def unique_tags(self) -> list[str]:
        """Get list of unique tags from all channels."""
        tags = set()
        for channel in self.channels:
            if channel.get("tags"):
                for t in channel["tags"].split(","):
                    clean_tag = t.strip()
                    if clean_tag:
                        tags.add(clean_tag)
        return sorted(list(tags))

    @rx.var
    def filtered_channels(self) -> list[Channel]:
        """Filter channels by search query and selected tag."""
        filtered = self.channels
        if self.selected_tag != "All":
            filtered = [
                c
                for c in filtered
                if self.selected_tag
                in [t.strip() for t in c.get("tags", "").split(",")]
            ]
        if self.search_query:
            query = self.search_query.lower()
            filtered = [c for c in filtered if query in c.get("name", "").lower()]
        return filtered

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def set_selected_tag(self, tag: str):
        self.selected_tag = tag

    @rx.var
    def m3u_content(self) -> str:
        """Generate M3U playlist content from scraped channels."""
        if not self.channels:
            return """#EXTM3U
# No channels found. Please run a scan first."""
        lines = ["#EXTM3U"]
        for channel in self.channels:
            if channel.get("status") == "success" and channel.get("m3u8_url"):
                name = channel.get("name", "Unknown").replace(",", " ")
                logo = channel.get("logo", "")
                group = channel.get("tags", "Uncategorized") or "Uncategorized"
                url = channel.get("m3u8_url", "")
                lines.append(
                    f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}'
                )
                lines.append(url)
        return """
""".join(lines)

    @rx.event
    def download_playlist(self):
        """Trigger download of the M3U playlist."""
        return rx.download(
            data=ScraperState.m3u_content, filename=f"playlist_{int(time.time())}.m3u"
        )

    @rx.event
    def toggle_auto_refresh(self):
        """Toggle auto-refresh mode."""
        self.auto_refresh = not self.auto_refresh
        if self.auto_refresh:
            self.add_log("Auto-refresh enabled. Scraper will run continuously.")
            if not self.is_scanning:
                return ScraperState.start_scan
        else:
            self.add_log("Auto-refresh disabled.")

    @rx.event
    def add_log(self, message: str):
        """Add a log message to the UI console."""
        timestamp = time.strftime("%H:%M:%S")
        self.logs.insert(0, f"[{timestamp}] {message}")
        if len(self.logs) > 50:
            self.logs.pop()

    @rx.event
    async def process_channel(
        self,
        session: aiohttp.ClientSession,
        idx: int,
        channel: Channel,
        sem: asyncio.Semaphore,
    ):
        """Process a single channel token extraction with concurrency limit."""
        async with sem:
            update_data = {}
            log_msg = ""
            try:
                stream_path = channel["stream_path"]
                player_url = f"http://tv.roarzone.info/player.php?stream={stream_path}"
                async with session.get(player_url) as response:
                    if response.status == 200:
                        text = await response.text()
                        m3u8_matches = re.findall(
                            "https?://[^\\s\\\"'<>]+\\.m3u8[^\\s\\\"'<>]*", text
                        )
                        if m3u8_matches:
                            token_url = m3u8_matches[0]
                            update_data = {
                                "m3u8_url": token_url,
                                "status": "success",
                                "last_updated": time.time(),
                            }
                        else:
                            update_data = {"status": "error"}
                            log_msg = f"✗ Error: No M3U8 found for {channel['name']}"
                    else:
                        update_data = {"status": "error"}
                        log_msg = (
                            f"✗ HTTP Error {response.status} for {channel['name']}"
                        )
            except Exception as e:
                logging.exception(f"Error processing channel {channel['name']}: {e}")
                update_data = {"status": "error"}
                log_msg = f"⚠ Exception for {channel['name']}: {str(e)[:30]}..."
            return (idx, update_data, log_msg)

    @rx.event(background=True)
    async def start_scan(self):
        """Start the scraping process using async/await for performance."""
        async with self:
            if self.is_scanning:
                return
            self.is_scanning = True
            self.scan_progress = 0
            self.channels = []
            self.logs = []
            self.scan_status_message = "Initializing async scraper..."
            self.add_log("Starting new scan session (Async Mode)...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "http://tv.roarzone.info/",
            }
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(
                headers=headers, timeout=timeout
            ) as session:
                async with self:
                    self.add_log("Fetching main channel list...")
                async with session.get("http://tv.roarzone.info/") as response:
                    response.raise_for_status()
                    html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")
                channel_cards = soup.find_all("div", class_="channel-card")
                extracted_channels = []
                for idx, card in enumerate(channel_cards):
                    stream_path = card.get("data-stream", "")
                    title = card.get("data-title", "")
                    tags = card.get("data-tags", "")
                    img = card.find("img")
                    logo = img.get("src", "") if img else ""
                    if logo and (not logo.startswith("http")):
                        logo = f"http://tv.roarzone.info/{logo}"
                    if not title and img:
                        title = img.get("alt", f"Channel {idx + 1}")
                    if stream_path:
                        extracted_channels.append(
                            {
                                "id": f"ch_{idx}_{int(time.time())}",
                                "name": title,
                                "logo": logo,
                                "stream_path": stream_path,
                                "tags": tags,
                                "m3u8_url": "",
                                "status": "pending",
                                "last_updated": 0.0,
                            }
                        )
                async with self:
                    self.channels = extracted_channels
                    self.total_channels = len(extracted_channels)
                    self.scan_status_message = f"Found {self.total_channels} channels. Starting concurrent token extraction..."
                    self.add_log(
                        f"Parsed {self.total_channels} channels. Launching tasks..."
                    )
                sem = asyncio.Semaphore(75)
                tasks = [
                    self.process_channel(session, i, c, sem)
                    for i, c in enumerate(extracted_channels)
                ]
                completed = 0
                pending_updates = {}
                pending_logs = []
                for future in asyncio.as_completed(tasks):
                    idx, update_data, log_msg = await future
                    completed += 1
                    pending_updates[idx] = update_data
                    if log_msg:
                        pending_logs.append(log_msg)
                    if len(pending_updates) >= 50 or completed == self.total_channels:
                        async with self:
                            current_channels = list(self.channels)
                            for i, data in pending_updates.items():
                                current_channels[i].update(data)
                            self.channels = current_channels
                            if pending_logs:
                                timestamp = time.strftime("%H:%M:%S")
                                new_logs = [
                                    f"[{timestamp}] {msg}" for msg in pending_logs
                                ] + self.logs
                                self.logs = new_logs[:50]
                            self.scan_progress = int(
                                completed / self.total_channels * 100
                            )
                            self.scan_status_message = (
                                f"Scanning... {completed}/{self.total_channels}"
                            )
                        pending_updates = {}
                        pending_logs = []
                async with self:
                    self.is_scanning = False
                    self.last_full_scan = time.time()
                    self.scan_status_message = "Scan complete."
                    self.add_log("Async scan completed successfully.")
                if self.auto_refresh:
                    async with self:
                        self.add_log("Auto-refresh active. Waiting 60s...")
                    await asyncio.sleep(60)
                    return ScraperState.start_scan
        except Exception as e:
            async with self:
                self.is_scanning = False
                self.scan_status_message = f"Error: {str(e)}"
                self.add_log(f"CRITICAL ERROR: {str(e)}")
                logging.exception("Async scan failed")