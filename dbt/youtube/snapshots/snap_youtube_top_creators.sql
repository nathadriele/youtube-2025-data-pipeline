{% snapshot snap_youtube_top_creators %}
{{
    config(
        target_schema='snapshots',
        unique_key='youtuber',
        strategy='check',
        check_cols=['subscribers', 'engagement_score', 'total_videos', 'content_value_index'],
    )
}}

select
    youtuber,
    channel_name,
    subscribers,
    total_videos,
    engagement_score,
    content_value_index,
    metaverse_integration_level,
    neural_interface_compatible
from {{ ref('youtube_top_creators') }}

{% endsnapshot %}
