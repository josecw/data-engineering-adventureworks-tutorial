with source as (
    select * from {{ source('raw_sales', 'salesorderdetail') }}
),
renamed as (
    select
        salesorderdetailid                        as order_detail_id,
        salesorderid                             as order_id,
        carriertrackingnumber                    as carrier_tracking_number,
        orderqty                                 as quantity,
        productid                                as product_id,
        specialofferid                           as special_offer_id,
        unitprice                                as unit_price,
        unitpricediscount                        as unit_price_discount,
        (unitprice * unitpricediscount)          as discount_amount,
        (unitprice * (1 - unitpricediscount) * orderqty) as line_total,
        _sdc_received_at                         as loaded_at
    from source
    where salesorderid is not null
)
select * from renamed
