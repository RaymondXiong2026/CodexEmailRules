import httpx

from app.core.config import get_settings

settings = get_settings()


class ERPClient:
    async def push(self, payload: dict) -> None:
        headers = {"Authorization": f"Bearer {settings.erp_api_key}"}
        async with httpx.AsyncClient(timeout=settings.erp_timeout_seconds) as client:
            resp = await client.post(f"{settings.erp_base_url}/email-events", json=payload, headers=headers)
            resp.raise_for_status()
