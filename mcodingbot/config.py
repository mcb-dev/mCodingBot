import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, cast

_ALWAYS_SAVE = ["discord_token"]


@dataclass
class Config:
    discord_token: str = "DISCORD_TOKEN"

    def save(self) -> None:
        pth = Path("config.json")

        dct = asdict(self)
        tosave: dict[str, Any] = {}
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
