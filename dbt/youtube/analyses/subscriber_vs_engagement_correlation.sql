-- Analysis: Subscriber concentration analysis by neural interface compatibility
-- Shows how subscriber distribution varies between neural-compatible and non-compatible channels

with base as (
    select
        neural_interface_compatible,
        subscribers,
        engagement_score
    from {{ ref('stg_youtube_data') }}
    where subscribers is not null
),

ranked as (
    select
        neural_interface_compatible,
        subscribers,
        engagement_score,
        row_number() over (
            partition by neural_interface_compatible
            order by subscribers desc
        ) as rank_within_group
    from base
)

select
    neural_interface_compatible,
    count(*) as total_creators,
    sum(subscribers) as total_subscribers,
    round(avg(subscribers), 2) as avg_subscribers,
    round(
        sum(case when rank_within_group <= 10 then subscribers else 0 end)::numeric
        / nullif(sum(subscribers), 0) * 100, 2
    ) as top_10_pct_share,
    max(subscribers) as max_subscribers,
    min(subscribers) as min_subscribers
from ranked
group by neural_interface_compatible
order by total_subscribers desc
