with customer as (
    select * from {{ ref('stg_person__customer') }}
),
enriched as (
    select
        customer_id,
        person_id,
        store_id,
        territory_id,
        account_number,
        first_name,
        last_name,
        full_name,
        email_promotion,
        demographics,
        loaded_at,
        row_number() over (partition by customer_id order by loaded_at desc) as rn
    from customer
)
select
    customer_id,
    person_id,
    store_id,
    territory_id,
    account_number,
    first_name,
    last_name,
    full_name,
    email_promotion,
    demographics,
    loaded_at as valid_from
from enriched
where rn = 1
