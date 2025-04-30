import aiohttp
import os
from typing import List, Dict, Optional


class BrevoMailer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.brevo.com/v3/smtp/email"
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @staticmethod
    def make_contact(email: str, name: Optional[str] = None) -> Dict[str, str]:
        contact = {"email": email}
        if name:
            contact["name"] = name
        return contact

    def _load_template(self, name: str) -> str:
        path = os.path.join("templates", "emails", f"{name}.html")
        if not os.path.isfile(path):
            raise ValueError(f"Template '{name}' not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _build_payload(
        self,
        to: List[Dict[str, str]],
        sender: Dict[str, str],
        subject: Optional[str] = None,
        reply_to: Optional[Dict[str, str]] = None,
        template_id: Optional[int] = None,
        template_name: Optional[str] = None,
        html_content: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict:
        content_options = [bool(template_id), bool(template_name), bool(html_content)]
        if sum(content_options) != 1:
            raise ValueError(
                "Provide exactly one of: template_id, template_name, or html_content"
            )

        payload = {"to": to, "sender": sender}

        if template_id:
            payload["templateId"] = template_id
            if params:
                payload["params"] = params
        elif template_name:
            payload["htmlContent"] = self._load_template(template_name)
            if not subject:
                raise ValueError(
                    "Subject is required when using htmlContent (via template_name)."
                )
            payload["subject"] = subject
        elif html_content:
            payload["htmlContent"] = html_content
            if not subject:
                raise ValueError("Subject is required when using raw html_content.")
            payload["subject"] = subject

        if reply_to:
            payload["replyTo"] = reply_to
        if headers:
            payload["headers"] = headers
        if tags:
            payload["tags"] = tags

        return payload

    async def send_email(
        self,
        to: List[Dict[str, str]],
        sender: Dict[str, str],
        subject: Optional[str] = None,
        reply_to: Optional[Dict[str, str]] = None,
        template_id: Optional[int] = None,
        template_name: Optional[str] = None,
        html_content: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict:
        body = self._build_payload(
            to=to,
            sender=sender,
            subject=subject,
            reply_to=reply_to,
            template_id=template_id,
            template_name=template_name,
            html_content=html_content,
            params=params,
            tags=tags,
            headers=headers,
        )

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.base_url, json=body, headers=self.headers
                ) as response:
                    if response.status != 201:
                        content = await response.text()
                        raise Exception(f"Email failed: {response.status} - {content}")
                    return await response.json()
            except aiohttp.ClientError as e:
                raise Exception(f"HTTP error: {str(e)}")
