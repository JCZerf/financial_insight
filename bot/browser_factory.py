from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from bot.identity import ScrapingIdentity


@dataclass
class BrowserFactory:
    """Fábrica base para navegador Playwright usado no scraping."""

    headless: bool = True
    timeout_ms: int = 30_000
    slow_mo: int = 0
    viewport_width: int = 1366
    viewport_height: int = 768
    locale: str = "pt-BR"
    timezone_id: str = "America/Sao_Paulo"
    extra_context_options: Dict[str, Any] = field(default_factory=dict)

    _playwright: Optional[Playwright] = field(init=False, default=None)
    _browser: Optional[Browser] = field(init=False, default=None)
    _context: Optional[BrowserContext] = field(init=False, default=None)

    def start(self) -> BrowserContext:
        """Inicializa Playwright + Browser + Context com identidade de scraping."""
        if self._context:
            return self._context

        identity_headers = ScrapingIdentity.get_full_identity()
        user_agent = identity_headers["User-Agent"]
        extra_http_headers = {
            key: value for key, value in identity_headers.items() if key != "User-Agent"
        }

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )
        self._context = self._browser.new_context(
            user_agent=user_agent,
            viewport={"width": self.viewport_width, "height": self.viewport_height},
            locale=self.locale,
            timezone_id=self.timezone_id,
            extra_http_headers=extra_http_headers,
            **self.extra_context_options,
        )
        self._context.set_default_timeout(self.timeout_ms)
        self._context.set_default_navigation_timeout(self.timeout_ms)
        return self._context

    def new_page(self) -> Page:
        """Retorna uma nova página dentro do contexto padrão."""
        context = self.start()
        return context.new_page()

    def close(self) -> None:
        """Fecha recursos do navegador de forma segura."""
        if self._context:
            self._context.close()
            self._context = None

        if self._browser:
            self._browser.close()
            self._browser = None

        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    def __enter__(self) -> "BrowserFactory":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
