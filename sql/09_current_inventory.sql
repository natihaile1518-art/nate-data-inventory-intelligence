-- ============================================================
-- FILE: 09_current_inventory.sql
-- PROJECT: Nate Data — Small Business Intelligence System
-- PURPOSE: Calculate current stock from all transactions
-- ============================================================

USE nate_data;

-- ============================================================
-- QUERY: Current inventory for all products at Shop 1
-- Formula: opening_stock + purchases - sales + adjustments
-- ============================================================
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    p.specification,

    -- Opening stock from the physical count
    COALESCE(snap.opening_qty, 0)          AS opening_stock,

    -- Total units purchased after opening
    COALESCE(purch.purchased_qty, 0)       AS purchased,

    -- Total units sold
    COALESCE(sold.sold_qty, 0)             AS sold,

    -- Current stock = opening + purchased - sold
    COALESCE(snap.opening_qty, 0)
    + COALESCE(purch.purchased_qty, 0)
    - COALESCE(sold.sold_qty, 0)           AS current_stock

FROM products p
JOIN categories c ON p.category_id = c.category_id

-- Opening snapshot
LEFT JOIN (
    SELECT product_id, SUM(quantity) AS opening_qty
    FROM inventory_snapshots
    WHERE location_id = 1
    GROUP BY product_id
) snap ON p.product_id = snap.product_id

-- Purchases after opening stock (exclude opening stock)
LEFT JOIN (
    SELECT pi.product_id, SUM(pi.quantity) AS purchased_qty
    FROM purchase_items pi
    JOIN purchases pu ON pi.purchase_id = pu.purchase_id
    WHERE pu.location_id = 1
      AND pu.supplier_name != 'Opening Stock'
    GROUP BY pi.product_id
) purch ON p.product_id = purch.product_id

-- Sales
LEFT JOIN (
    SELECT si.product_id, SUM(si.quantity_sold) AS sold_qty
    FROM sale_items si
    JOIN sales s ON si.sale_id = s.sale_id
    WHERE s.location_id = 1
    GROUP BY si.product_id
) sold ON p.product_id = sold.product_id

WHERE p.is_active = 1
ORDER BY c.category_name, p.product_name
LIMIT 20;
