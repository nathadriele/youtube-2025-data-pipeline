-- Custom test: Ensure all engagement scores are positive (greater than zero)
-- This catches data quality issues where engagement scores could be invalid.

select count(*)
from {{ ref('stg_youtube_data') }}
where engagement_score <= 0
