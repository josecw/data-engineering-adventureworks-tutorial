with source as (
    select * from {{ source('raw_sales', 'salesorderheader') }}
),
renamed as (
    select
        salesorderid                                as order_id,
        revisionnumber                              as revision_number,
        orderdate::date                             as order_date,
        duedate::date                               as due_date,
        shipdate::date                              as ship_date,
        status                                      as order_status,
        case
            when onlineorderflag = true then 'Online'
            else 'Reseller'
        end                                         as order_channel,
        customerid                                  as customer_id,
        salespersonid                               as salesperson_id,
        territoryid                                 as territory_id,
        billtoaddressid                             as bill_to_address_id,
        shiptoaddressid                             as ship_to_address_id,
        subtotal                                    as subtotal,
        taxamt                                      as tax_amount,
        freight                                     as freight,
        totaldue                                    as total_due,
        _sdc_received_at                            as loaded_at
    from source
    where orderdate is not null
)
select * from renamed
