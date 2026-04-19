-- Custom test: Ensure neural_interface_compatible contains only boolean-like values
-- Accepted values: True, False, Yes, No, Unknown

select count(*)
from {{ ref('stg_youtube_data') }}
where lower(trim(neural_interface_compatible)) not in ('true', 'false', 'yes', 'no', 'unknown')
