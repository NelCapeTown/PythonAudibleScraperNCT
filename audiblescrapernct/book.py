from dataclasses import dataclass

@dataclass(slots=True)
class Book:
    title: str
    author: str
    narrator: str
    description: str
    cover_image_url: str
    series: str = ""
