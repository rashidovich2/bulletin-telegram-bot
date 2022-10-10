from dataclasses import dataclass


@dataclass
class Ad:
    id: int
    user_id: int
    ad_type: str
    category: str
    cost: int
    description: str
    media_group: any
    published: int

    def set_media_group(self, v):
        self.media_group = v
