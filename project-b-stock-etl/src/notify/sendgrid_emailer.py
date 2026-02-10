from __future__ import annotations

import base64
import mimetypes
import os
from dataclasses import dataclass
from typing import Iterable, Optional

import requests


@dataclass(frozen=True)
class EmailConfig:
    api_key: str
    email_from: str
    email_to: str


def _require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def load_email_config() -> EmailConfig:
    """Load SendGrid config from env vars."""
    return EmailConfig(
        api_key=_require_env("SENDGRID_API_KEY"),
        email_from=_require_env("EMAIL_FROM"),
        email_to=_require_env("EMAIL_TO"),
    )


def _mime_type(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    return mt or "application/octet-stream"


def send_email(
    subject: str,
    body_text: str,
    attachments: Optional[Iterable[str]] = None,
    config: Optional[EmailConfig] = None,
) -> None:
    """Send a plain-text email via SendGrid with optional attachments."""
    cfg = config or load_email_config()

    payload: dict = {
        "personalizations": [{"to": [{"email": cfg.email_to}]}],
        "from": {"email": cfg.email_from},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body_text}],
    }

    att_list = []
    for path in attachments or []:
        if not os.path.isfile(path):
            raise RuntimeError(f"Attachment not found: {path}")
        with open(path, "rb") as f:
            raw = f.read()
        att_list.append(
            {
                "content": base64.b64encode(raw).decode("utf-8"),
                "type": _mime_type(path),
                "filename": os.path.basename(path),
                "disposition": "attachment",
            }
        )

    if att_list:
        payload["attachments"] = att_list

    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {cfg.api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if resp.status_code not in (200, 202):
        raise RuntimeError(f"SendGrid send failed: {resp.status_code} {resp.text}")
