-- Define primary keys
ALTER TABLE dim_customers ADD PRIMARY KEY (customer_id);
ALTER TABLE dim_geography ADD PRIMARY KEY (geography_key);
ALTER TABLE dim_products  ADD PRIMARY KEY (product_key);
ALTER TABLE dim_shipping  ADD PRIMARY KEY (shipping_key);
ALTER TABLE dim_statuses  ADD PRIMARY KEY (status_key);
ALTER TABLE dim_calendar ADD PRIMARY KEY (order_date);


-- Define forein keys
ALTER TABLE fact_sales 
    ADD CONSTRAINT fk_fact_customer FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    ADD CONSTRAINT fk_fact_geography FOREIGN KEY (geography_key) REFERENCES dim_geography(geography_key),
    ADD CONSTRAINT fk_fact_product FOREIGN KEY (product_key) REFERENCES dim_products(product_key),
    ADD CONSTRAINT fk_fact_shipping FOREIGN KEY (shipping_key) REFERENCES dim_shipping(shipping_key),
    ADD CONSTRAINT fk_fact_status FOREIGN KEY (status_key) REFERENCES dim_statuses(status_key),
    ADD CONSTRAINT fk_fact_calendar FOREIGN KEY (order_date) REFERENCES dim_calendar(order_date);


-- Ad hoc validation query 
SELECT 
    p.category AS product_category,
    g.country AS customer_country,
    COUNT(f.order_id) AS total_orders,
    ROUND(SUM(f.revenue)::numeric, 2) AS clean_net_revenue,
    ROUND(SUM(f.profit)::numeric, 2) AS clean_net_profit
FROM fact_sales f
-- join folders using keys
JOIN dim_products p ON f.product_key = p.product_key
JOIN dim_geography g ON f.geography_key = g.geography_key
JOIN dim_statuses s ON f.status_key = s.status_key
-- Enforce your accounting rulebook ie, filters for complete orders
WHERE s.is_revenue_earned = 1
GROUP BY p.category, g.country
ORDER BY clean_net_revenue DESC;

ALTER TABLE dim_calendar ADD PRIMARY KEY (order_date);
