{{ dbt_date.get_date_dimension(
    start_date="2011-01-01",
    end_date="dateadd('year', 5, current_date)"
) }}
