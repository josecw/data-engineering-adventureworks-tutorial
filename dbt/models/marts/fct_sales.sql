with orders as (
    select * from {{ ref('stg_sales__orders') }}
),
order_detail as (
    select * from {{ ref('stg_sales__order_detail') }}
),
customer as (
    select * from {{ ref('dim_customer') }}
),
product as (
    select * from {{ ref('dim_product') }}
),
territory as (
    select * from {{ ref('dim_territory') }}
),
joined as (
    select
        o.order_id,
        o.revision_number,
        o.order_date,
        o.due_date,
        o.ship_date,
        o.order_status,
        o.order_channel,
        o.customer_id,
        c.full_name as customer_name,
        c.territory_id as customer_territory_id,
        t.territory_name,
        t.sales_group,
        od.order_detail_id,
        od.product_id,
        p.product_name,
        p.category_name,
        p.subcategory_name,
        od.quantity,
        od.unit_price,
        od.unit_price_discount,
        od.discount_amount,
        od.line_total,
        o.subtotal,
        o.tax_amount,
        o.freight,
        o.total_due
    from orders o
    inner join order_detail od
        on o.order_id = od.order_id
    left join customer c
        on o.customer_id = c.customer_id
    left join product p
        on od.product_id = p.product_id
    left join territory t
        on o.territory_id = t.territory_id
)
select * from joined
