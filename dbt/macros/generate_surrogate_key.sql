{% macro generate_surrogate_key(column_names) %}
    {% if column_names is string and '.' in column_names %}
        {{ return(dbt_utils.surrogate_key(column_names)) }}
    {% elif column_names is iterable and column_names is not string %}
        {% set columns = column_names | join(', ') %}
        {{ return(dbt_utils.surrogate_key(columns)) }}
    {% else %}
        {{ return(dbt_utils.surrogate_key(column_names)) }}
    {% endif %}
{% endmacro %}
