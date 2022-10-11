import json
from typing import List

from tgbot.models.ad import Ad


class Repo:
    """Db abstraction layer"""

    def __init__(self, conn):
        self.conn = conn

    # ads
    async def add_ad(self, user_id, ad_type, category, cost, description, media_group=None) -> Ad:
        """Store user in DB, ignore duplicates"""
        if media_group is None:
            media_group = []

        row = await self.conn.fetchrow(
            "INSERT INTO ads(user_id, ad_type, category, cost, description, media_group) "
            "VALUES ($1, $2, $3, $4, $5, $6) "
            "RETURNING id, user_id, ad_type, category, cost, description, media_group, published",
            user_id,
            ad_type,
            category,
            int(cost),
            description,
            json.dumps(media_group)
        )

        ad = Ad(**row)

        ad.set_media_group(json.loads(ad.media_group))

        return ad

    async def update_ad(self, ad_id, ad_type, category, cost, description, media_group=None) -> Ad:
        if media_group is None:
            media_group = []

        row = await self.conn.fetchrow(
            "UPDATE ads SET ad_type = $1, category = $2, cost = $3, description = $4, media_group = $5 "
            "WHERE id = $6 "
            "RETURNING id, user_id, ad_type, category, cost, description, media_group, published",
            ad_type,
            category,
            int(cost),
            description,
            json.dumps(media_group),
            int(ad_id)
        )

        ad = Ad(**row)

        ad.set_media_group(json.loads(ad.media_group))

        return ad

    async def publish_ad(self, ad_id, message_id):
        await self.conn.execute(
            "UPDATE ads SET published = $1 "
            "WHERE id = $2 ",
            int(message_id),
            int(ad_id)
        )

    async def revoke_ad(self, ad_id):
        await self.conn.execute(
            "UPDATE ads SET published = 0 "
            "WHERE id = $1 ",
            int(ad_id)
        )

    async def get_ad(self, ad_id) -> Ad:
        row = await self.conn.fetchrow(
            "SELECT id, user_id, ad_type, category, cost, description, media_group, published "
            "FROM ads "
            "WHERE id = $1",
            int(ad_id)
        )

        ad = Ad(**row)

        ad.set_media_group(json.loads(ad.media_group))

        return ad

    async def get_last_user_ad(self, user_id) -> Ad:
        row = await self.conn.fetchrow(
            "SELECT id, user_id, ad_type, category, cost, description, media_group, published "
            "FROM ads "
            "WHERE user_id = $1 "
            "ORDER BY id DESC",
            int(user_id)
        )

        ad = Ad(**row)

        ad.set_media_group(json.loads(ad.media_group))

        return ad
