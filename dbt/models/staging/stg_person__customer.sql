with customer as (
    select * from {{ source('raw_sales_customer', 'customer') }}
),
person as (
    select * from {{ source('raw_person', 'person') }}
),
joined as (
    select
        c.customerid                                as customer_id,
        c.personid                                  as person_id,
        c.storeid                                   as store_id,
        c.territoryid                               as territory_id,
        c.accountnumber                             as account_number,
        p.firstname                                 as first_name,
        p.lastname                                  as last_name,
        concat(p.firstname, ' ', p.lastname)        as full_name,
        p.emailpromotion                             as email_promotion,
        p.demographics::json                        as demographics,
        c._sdc_received_at                          as loaded_at
    from customer c
    left join person p
        on c.personid = p.businessentityid
)
select * from joined
