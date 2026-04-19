{{ config(materialized='table') }}

select
    youtuber,
    coalesce(category, 'Unknown') as category,
    coalesce(country, 'Unknown') as country,
    subscribers,
    video_views
from {{ ref('stg_youtube_data') }}
where youtuber is not null
  and subscribers is not null
  and video_views is not null
order by subscribers desc, video_views desc