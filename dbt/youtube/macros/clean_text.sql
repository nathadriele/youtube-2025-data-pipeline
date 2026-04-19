{% macro clean_text(column_name) %}
/**
  Clean a text column by trimming whitespace and converting to lowercase.
  Usage: {{ clean_text('column_name') }}
*/
lower(trim({{ column_name }}))
{% endmacro %}
