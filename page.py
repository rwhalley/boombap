from dataclasses import dataclass

@dataclass
class Sample:
    name: str
    path: str
    vol: int = 128
    pitch: float = 1.0

@dataclass
class Kit:
    name: str
    path: str
    samples: list
    volumes: list

@dataclass
class Page:
    name: str
    path: str
    kits: list




