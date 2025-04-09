{{ config(materialized='table') }}

select
    category,
    country,
    count(*) as total_creators,
    avg(subscribers) as avg_subscribers,
    avg(video_views) as avg_views
from {{ ref('stg_youtube_data') }}
group by category, country
