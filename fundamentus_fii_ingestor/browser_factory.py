from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

try:
    from fundamentus_fii_ingestor.identity import ScrapingIdentity
except ModuleNotFoundError:
    from identity import ScrapingIdentity


@dataclass
class BrowserFactory:
    # Execução do browser 
    
    headless: bool = True
    timeout_ms: int = 30_000
    slow_mo: int = 0

    # Fallback caso o perfil de identidade não informe esses campos.
    viewport_width: int = 1366
    viewport_height: int = 768
    locale: str = "pt-BR"
    timezone_id: str = "America/Sao_Paulo"
    extra_context_options: Dict[str, Any] = field(default_factory=dict)

    _playwright: Optional[Playwright] = field(init=False, default=None)
    _browser: Optional[Browser] = field(init=False, default=None)
    _context: Optional[BrowserContext] = field(init=False, default=None)

    async def start(self) -> BrowserContext:
        """Inicializa Playwright + Browser + Context com identidade de scraping."""
        if self._context:
            return self._context

        identity_profile = ScrapingIdentity.get_browser_profile()
        user_agent = identity_profile["user_agent"]
        extra_http_headers = identity_profile["headers"]
        viewport = identity_profile.get(
            "viewport",
            {"width": self.viewport_width, "height": self.viewport_height},
        )
        locale = identity_profile.get("locale", self.locale)
        timezone_id = identity_profile.get("timezone_id", self.timezone_id)

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )
            self._context = await self._browser.new_context(
                user_agent=user_agent,
                viewport=viewport,
                locale=locale,
                timezone_id=timezone_id,
                extra_http_headers=extra_http_headers,
                **self.extra_context_options,
            )
            self._context.set_default_timeout(self.timeout_ms)
            self._context.set_default_navigation_timeout(self.timeout_ms)
            return self._context
        except Exception:
            await self.close()
            raise

    async def new_page(self) -> Page:
        """Retorna uma nova página dentro do contexto padrão."""
        context = await self.start()
        return await context.new_page()

    async def close(self) -> None:
        """Fecha recursos do navegador de forma segura."""
        if self._context:
            try:
                await self._context.close()
            finally:
                self._context = None

        if self._browser:
            try:
                await self._browser.close()
            finally:
                self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            finally:
                self._playwright = None

    async def __aenter__(self) -> "BrowserFactory":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
