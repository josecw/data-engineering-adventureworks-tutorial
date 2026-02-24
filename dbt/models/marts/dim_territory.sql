with territory as (
    select * from {{ source('raw_sales', 'salesterritory') }}
),
renamed as (
    select
        territoryid                             as territory_id,
        name                                   as territory_name,
        countryregioncode                      as country_region_code,
        group                                  as sales_group,
        salesytd                               as sales_ytd,
        saleslastyear                          as sales_last_year,
        costytd                                as cost_ytd,
        costlastyear                           as cost_last_year,
        rowguid,
        modifieddate                           as modified_at,
        _sdc_received_at                       as loaded_at
    from territory
)
select * from renamed
