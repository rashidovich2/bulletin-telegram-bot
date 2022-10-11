CREATE TABLE IF NOT EXISTS ads (
  id serial not null primary key,
  user_id bigint,
  description text,
  "cost" bigint,
  ad_type text,
  category text,
  media_group jsonb,
  published int default 0
);

ALTER TABLE ads
ADD COLUMN IF NOT EXISTS publish_msg_ids jsonb;

ALTER TABLE ads
ALTER COLUMN publish_msg_ids SET default '[]'::jsonb;