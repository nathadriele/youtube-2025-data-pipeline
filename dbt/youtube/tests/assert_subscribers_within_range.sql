-- Custom test: Ensure subscriber counts are within a reasonable range
-- Flags rows where subscribers exceed 1 billion (likely data quality issue)

select count(*)
from {{ ref('stg_youtube_data') }}
where subscribers > 1000000000
