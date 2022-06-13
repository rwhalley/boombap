from dataclasses import dataclass

@dataclass
class Sample:
    name: str
    path: str

@dataclass
class Kit:
    name: str
    path: str
    samples: list

@dataclass
class Page:
    name: str
    path: str
    kits: list




