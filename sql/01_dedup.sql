WITH ranked AS 
    (
        Select *,
        ROW_NUMBER() over (partition by symbol, open_time ORDER BY ingested_at DESC) as row_nr  
        from raw_candles
    )
Select * from ranked where row_nr = 1