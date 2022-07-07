import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, cast

_ALWAYS_SAVE = ["discord_token"]


@dataclass
class Config:
    discord_token: str = "DISCORD_TOKEN"
    theme: int = 0x0B7CD3

    mcoding_server: int = -1
    sub_count_channel: int = -1
    view_count_channel: int = -1
    member_count_channel: int = -1

    mcoding_yt_id: str = ""
    yt_api_key: str = ""

    mcoding_youtube: str = (
        "https://www.youtube.com/channel/UCaiL2GDNpLYH6Wokkk1VNcg"
    )
    mcoding_repo: str = "https://github.com/mCodingLLC/VideosSampleCode"
    mcodingbot_repo: str = "https://github.com/mcb-dev/mCodingBot"

    def save(self) -> None:
        pth = Path("config.json")

        dct = asdict(self)
        tosave: Dict[str, Any] = {}
        defaults = self.__class__()
        for k, v in dct.items():
            if k not in _ALWAYS_SAVE and getattr(defaults, k) == v:
                continue

            tosave[k] = v

        with pth.open("w+") as f:
            f.write(json.dumps(tosave, indent=4))

    @classmethod
    def load(cls) -> "Config":
        pth = Path("config.json")

        if not pth.exists():
            c = Config()
        else:
            keys = set(inspect.signature(Config).parameters)
            with pth.open("r") as f:
                c = Config(
                    **{
                        k: v
                        for k, v in cast(
                            "Dict[Any, Any]", json.loads(f.read())
                        ).items()
                        if k in keys
                    }
                )

        c.save()
        return c


CONFIG = Config.load()
