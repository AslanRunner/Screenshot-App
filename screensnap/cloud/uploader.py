"""
Cloud upload management via tmpfiles.org with background worker support.
"""

import os
import json
import requests
import pyperclip
from screensnap.config import HISTORY_FILE


class CloudUploader:
    def __init__(self):
        self.history = self._load_history()

    def _load_history(self) -> dict:
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass

    def is_shared(self, fpath: str) -> bool:
        return fpath in self.history

    def get_shared_url(self, fpath: str) -> str | None:
        return self.history.get(fpath)

    def upload_file(self, fpath: str) -> str:
        """Uploads file to tmpfiles.org, saves link to history, copies to clipboard and returns direct url."""
        with open(fpath, "rb") as f:
            response = requests.post(
                "https://tmpfiles.org/api/v1/upload",
                files={"file": f},
                timeout=25
            )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and "data" in data and "url" in data["data"]:
                raw_url = data["data"]["url"]
                direct_url = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                self.history[fpath] = direct_url
                self._save_history()
                pyperclip.copy(direct_url)
                return direct_url
            else:
                raise RuntimeError(data.get("message", "API response error"))
        else:
            raise RuntimeError(f"HTTP Status {response.status_code}")

    def delete_history_entry(self, fpath: str):
        if fpath in self.history:
            del self.history[fpath]
            self._save_history()