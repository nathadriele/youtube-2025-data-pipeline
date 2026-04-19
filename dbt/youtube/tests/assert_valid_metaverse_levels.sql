-- Custom test: Ensure metaverse_integration_level contains only expected values
-- Accepted values: Full, Advanced, Partial, Basic, None, Unknown

select count(*)
from {{ ref('stg_youtube_data') }}
where lower(trim(metaverse_integration_level)) not in ('full', 'advanced', 'partial', 'basic', 'none', 'unknown')
