"""Web automation — browser control, search, scraping."""

from __future__ import annotations

import urllib.parse
import webbrowser
from typing import Optional

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.automation.web")


class WebAutomation:
    """Automate web browser tasks."""

    def __init__(self) -> None:
        self._browser = None

    def google_search(self, query: str) -> dict[str, str]:
        """Open a Google search in the default browser."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded}"
        return self.open_url(url)

    def open_url(self, url: str) -> dict[str, str]:
        """Open a URL in the default browser."""
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        logger.info(f"Opening URL: {url}")
        try:
            webbrowser.open(url)
            return {"status": "success", "url": url}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def open_youtube(self, query: Optional[str] = None) -> dict[str, str]:
        """Open YouTube, optionally searching for a query."""
        if query:
            encoded = urllib.parse.quote_plus(query)
            url = f"https://www.youtube.com/results?search_query={encoded}"
        else:
            url = "https://www.youtube.com"
        return self.open_url(url)

    def open_site(self, site_name: str) -> dict[str, str]:
        """Open a well-known website by name."""
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
            "gmail": "https://mail.google.com",
            "drive": "https://drive.google.com",
            "twitter": "https://twitter.com",
            "reddit": "https://www.reddit.com",
            "linkedin": "https://www.linkedin.com",
            "wikipedia": "https://www.wikipedia.org",
            "chatgpt": "https://chat.openai.com",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
        }
        url = sites.get(site_name.lower())
        if url:
            return self.open_url(url)
        return self.open_url(f"https://www.{site_name}.com")

    async def scrape_text(self, url: str) -> dict[str, str]:
        """Fetch and extract text from a web page."""
        try:
            import httpx
            from bs4 import BeautifulSoup

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # Truncate to avoid memory issues
            text = text[:5000]
            return {"status": "success", "url": url, "text": text}
        except ImportError:
            return {"status": "error", "message": "beautifulsoup4 or httpx not installed"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    async def download_file(self, url: str, save_path: str) -> dict[str, str]:
        """Download a file from a URL."""
        try:
            from pathlib import Path

            import httpx

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            Path(save_path).write_bytes(response.content)
            logger.info(f"Downloaded {url} -> {save_path}")
            return {"status": "success", "path": save_path, "size": len(response.content)}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
