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
    publish_msg_ids: any
    published: int

    def set_media_group(self, v):
        self.media_group = v

    def set_publish_msg_ids(self, v):
        self.publish_msg_ids = v
