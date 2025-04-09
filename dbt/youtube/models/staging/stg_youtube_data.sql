{{ config(materialized='view') }}

select
    "Youtuber" as youtuber,
    "Subscribers" as subscribers,
    "Video views" as video_views,
    "Category" as category,
    "Country" as country
from {{ source('public', 'youtube_2025_dataset') }}
