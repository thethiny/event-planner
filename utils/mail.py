import aiohttp
import asyncio
import os
from typing import List, Dict, Optional, Union


class BrevoMailer:
    def __init__(self, api_key: str):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Valid API key must be provided.")
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

    def _normalize_contact(self, entry: Union[str, Dict[str, str]]) -> Dict[str, str]:
        if isinstance(entry, str):
            return {"email": entry}
        elif isinstance(entry, dict):
            if "email" not in entry:
                raise ValueError("Contact dict must contain 'email' key.")
            return {
                "email": entry["email"],
                **({"name": entry["name"]} if "name" in entry else {}),
            }
        else:
            raise ValueError("Invalid contact format. Must be str or dict.")

    def _normalize_contact_field(self, field) -> List[Dict[str, str]]:
        if field is None or not field:
            raise ValueError(f"Passed empty field")
        if isinstance(field, (str, dict)):
            return [self._normalize_contact(field)]
        elif isinstance(field, list):
            return [self._normalize_contact(f) for f in field]
        else:
            raise ValueError("Invalid field type for contact list.")

    def _build_payload(
        self,
        to,
        sender,
        subject: Optional[str] = None,
        reply_to: Optional[Union[str, Dict]] = None,
        cc: Optional[Union[str, Dict, List]] = None,
        bcc: Optional[Union[str, Dict, List]] = None,
        template_id: Optional[int] = None,
        template_name: Optional[str] = None,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict:
        # Normalize contacts
        to = self._normalize_contact_field(to)
        sender = self._normalize_contact_field(sender)[0]
        reply_to = self._normalize_contact_field(reply_to)[0]
        cc = self._normalize_contact_field(cc)
        bcc = self._normalize_contact_field(bcc)

        # Validate content combinations
        content_fields = [bool(b) for b in [
            template_id,
            template_name,
            html_content,
            text_content,
        ]]
        if sum(content_fields) == 0:
            raise ValueError(
                "You must provide one of: template_id, template_name, html_content, or text_content"
            )
        if template_id and (template_name or html_content or text_content):
            raise ValueError(
                "template_id cannot be combined with template_name, html_content, or text_content"
            )

        payload = {"to": to, "sender": sender}

        if reply_to:
            payload["replyTo"] = reply_to
        if cc:
            payload["cc"] = cc
        if bcc:
            payload["bcc"] = bcc

        if template_id:
            payload["templateId"] = template_id
            if params:
                payload["params"] = params
        else:
            # Use template file if specified
            if template_name:
                html_content = self._load_template(template_name)

            if not subject:
                raise ValueError("Subject is required when not using templateId.")

            payload["subject"] = subject
            if html_content:
                payload["htmlContent"] = html_content
            if text_content:
                payload["textContent"] = text_content

        if headers:
            payload["headers"] = headers
        if tags:
            payload["tags"] = tags

        return payload

    async def send_email(
        self,
        to,
        sender,
        subject: Optional[str] = None,
        reply_to: Optional[Union[str, Dict]] = None,
        cc: Optional[Union[str, Dict, List]] = None,
        bcc: Optional[Union[str, Dict, List]] = None,
        template_id: Optional[int] = None,
        template_name: Optional[str] = None,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict:
        body = self._build_payload(
            to=to,
            sender=sender,
            subject=subject,
            reply_to=reply_to,
            cc=cc,
            bcc=bcc,
            template_id=template_id,
            template_name=template_name,
            html_content=html_content,
            text_content=text_content,
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
