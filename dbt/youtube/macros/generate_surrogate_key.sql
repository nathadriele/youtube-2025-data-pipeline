{% macro generate_surrogate_key(columns) %}
/**
  Generate a deterministic surrogate key by hashing a combination of columns.
  Uses MD5 for a compact, reproducible hash.
  Usage: {{ generate_surrogate_key(['channel_name', 'youtuber']) }}
*/
md5(concat({{ columns | join(", '|', ") }}))
{% endmacro %}
