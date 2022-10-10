CREATE TABLE ads (
  id serial not null primary key,
  user_id bigint,
  description text,
  "cost" bigint,
  ad_type text,
  category text,
  media_group jsonb,
  published int default 0
);