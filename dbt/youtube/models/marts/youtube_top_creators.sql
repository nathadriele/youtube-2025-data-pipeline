{{ config(materialized='table') }}

select
    youtuber,
    channel_name,
    coalesce(metaverse_integration_level, 'Unknown') as metaverse_integration_level,
    coalesce(neural_interface_compatible, 'Unknown') as neural_interface_compatible,
    subscribers,
    total_videos,
    engagement_score,
    content_value_index
from {{ ref('stg_youtube_data') }}
where youtuber is not null
  and subscribers is not null
  and engagement_score is not null
order by subscribers desc, engagement_score desc
