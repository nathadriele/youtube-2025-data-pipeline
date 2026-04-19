-- Analysis: Engagement distribution across metaverse integration levels
-- Provides statistical breakdown (min, max, avg, median) per level
-- Useful for understanding how metaverse integration correlates with engagement

with base as (
    select
        metaverse_integration_level,
        engagement_score
    from {{ ref('stg_youtube_data') }}
    where engagement_score is not null
)

select
    metaverse_integration_level,
    count(*) as creator_count,
    round(min(engagement_score), 2) as min_engagement,
    round(max(engagement_score), 2) as max_engagement,
    round(avg(engagement_score), 2) as avg_engagement,
    round(
        percentile_cont(0.5) within group (order by engagement_score), 2
    ) as median_engagement,
    round(
        percentile_cont(0.9) within group (order by engagement_score), 2
    ) as p90_engagement
from base
group by metaverse_integration_level
order by avg_engagement desc
