with product as (
    select * from {{ source('raw_production', 'product') }}
),
subcategory as (
    select * from {{ source('raw_production', 'productsubcategory') }}
),
category as (
    select * from {{ source('raw_production', 'productcategory') }}
),
enriched as (
    select
        p.productid                                as product_id,
        p.name                                     as product_name,
        p.productnumber                            as product_number,
        p.makeflag                                 as make_flag,
        p.finishedgoodsflag                        as finished_goods_flag,
        p.color                                    as color,
        p.safetystocklevel                         as safety_stock_level,
        p.reorderpoint                             as reorder_point,
        p.standardcost                             as standard_cost,
        p.listprice                                as list_price,
        p.size                                     as size,
        p.sizeunitmeasurecode                       as size_unit_measure_code,
        p.weightunitmeasurecode                    as weight_unit_measure_code,
        p.weight                                   as weight,
        p.daystomanufacture                        as days_to_manufacture,
        p.productline                              as product_line,
        p.class                                    as product_class,
        p.style                                    as product_style,
        ps.productsubcategoryid                    as subcategory_id,
        ps.name                                    as subcategory_name,
        pc.productcategoryid                       as category_id,
        pc.name                                    as category_name,
        p.sellstartdate::date                      as sell_start_date,
        p.sellenddate::date                        as sell_end_date,
        p.discontinueddate::date                   as discontinued_date,
        p._sdc_received_at                         as loaded_at
    from product p
    left join subcategory ps
        on p.productsubcategoryid = ps.productsubcategoryid
    left join category pc
        on ps.productcategoryid = pc.productcategoryid
)
select * from enriched
