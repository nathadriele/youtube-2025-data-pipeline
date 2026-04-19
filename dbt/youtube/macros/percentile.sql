{% macro percentile(column_name, percentile_value=0.5) %}
/**
  Calculate the approximate percentile for a numeric column.
  Uses PostgreSQL percentile_cont function.
  Usage: {{ percentile('subscribers', 0.9) }}
*/
percentile_cont({{ percentile_value }})
    within group (order by {{ column_name }})
{% endmacro %}
