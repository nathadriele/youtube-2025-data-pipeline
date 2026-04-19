{{ config(materialized='view') }}

select
    "channel_name" as channel_name,
    "youtuber" as youtuber,
    "subscribers" as subscribers,
    "total_videos" as total_videos,
    "engagement_score" as engagement_score,
    "content_value_index" as content_value_index,
    "metaverse_integration_level" as metaverse_integration_level,
    "neural_interface_compatible" as neural_interface_compatible
from {{ source('public', 'youtube_2025_dataset') }}
