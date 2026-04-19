{{ config(materialized='table') }}

select
    coalesce(neural_interface_compatible, 'Unknown') as neural_interface_compatible,
    count(*) as total_creators,
    round(avg(subscribers), 2) as avg_subscribers,
    round(avg(engagement_score), 2) as avg_engagement_score,
    round(avg(content_value_index), 2) as avg_content_value_index,
    max(subscribers) as max_subscribers,
    max(engagement_score) as max_engagement_score
from {{ ref('stg_youtube_data') }}
where subscribers is not null
  and engagement_score is not null
group by 1
