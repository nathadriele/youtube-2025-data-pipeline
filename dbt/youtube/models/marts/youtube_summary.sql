{{ config(materialized='table') }}

select
    coalesce(category, 'Unknown') as category,
    coalesce(country, 'Unknown') as country,
    count(*) as total_creators,
    round(avg(subscribers), 2) as avg_subscribers,
    round(avg(video_views), 2) as avg_views
from {{ ref('stg_youtube_data') }}
where subscribers is not null
  and video_views is not null
group by 1, 2