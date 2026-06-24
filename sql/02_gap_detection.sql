with days as(
        select distinct symbol , date_trunc('day', open_time) as day
        from raw_candles
    ),
    expected_minutes as (
        select symbol, gs as minute from days, generate_series(day, day+interval '23:59:00', '1 minute') as gs
    )

Select em.symbol, em.minute
from expected_minutes em
left join raw_candles c on em.minute = c.open_time
where c.open_time IS NULL
order by em.symbol, em.minute; 