-- ============================================================
-- FILE: 08_purchase_entry.sql
-- PROJECT: Nate Data — Small Business Intelligence System
-- PURPOSE: Template for recording stock purchases
-- ============================================================
-- WORKFLOW:
--   1. Owner/worker buys stock from supplier
--   2. Enter the purchase into this system
--   3. Inventory automatically increases when calculated
-- ============================================================

USE nate_data;

-- ============================================================
-- STEP 1: Create the purchase header
-- location_id: 1=Shop 1, 2=Shop 2, 3=Warehouse
-- user_id: 1=Natnael, 2=Ahmed, 3=Tsion
-- Replace all values with real purchase information
-- ============================================================
INSERT INTO purchases
    (location_id, user_id, purchase_date, supplier_name, notes)
VALUES (
    1,                   -- location: Shop 1
    1,                   -- entered by: Natnael (owner)
    '2026-08-21',        -- date of purchase
    'Addis Trading',     -- supplier name
    'Regular restock'    -- notes
);

-- ============================================================
-- STEP 2: Check the purchase_id that was just assigned
-- Note this ID — you will need it if you want to query later
-- ============================================================
SELECT LAST_INSERT_ID() AS new_purchase_id;

-- ============================================================
-- STEP 3: Insert purchase items
-- Replace LAST_INSERT_ID() with the actual ID from Step 2
-- if running these statements separately
-- One row per product purchased
-- ============================================================
INSERT INTO purchase_items
    (purchase_id, product_id, quantity, purchase_price_etb)
VALUES
    (LAST_INSERT_ID(), 'P0035', 20, 230.00),  -- Esmiz Spot BK x20
    (LAST_INSERT_ID(), 'P0063', 30, 230.00),  -- Tesla Spot BK x30
    (LAST_INSERT_ID(), 'P0078', 50, 300.00);  -- CHNT 1 Phase 10A x50

-- ============================================================
-- STEP 4: Verify the purchase was recorded correctly
-- Uses MAX(purchase_id) to get the most recently inserted one
-- ============================================================
SELECT
    pu.purchase_id,
    pu.purchase_date,
    pu.supplier_name,
    l.location_name,
    u.full_name                              AS purchased_by,
    p.product_name,
    p.specification,
    pi.quantity,
    pi.purchase_price_etb,
    (pi.quantity * pi.purchase_price_etb)    AS line_total_etb
FROM purchases pu
JOIN purchase_items pi ON pu.purchase_id = pi.purchase_id
JOIN products p        ON pi.product_id  = p.product_id
JOIN locations l       ON pu.location_id = l.location_id
JOIN users u           ON pu.user_id     = u.user_id
WHERE pu.purchase_id = (SELECT MAX(purchase_id)
                        FROM purchases
                        WHERE supplier_name != 'Opening Stock')
ORDER BY pi.item_id;

-- ============================================================
-- STEP 5: Calculate total cost of this purchase
-- ============================================================
SELECT
    pu.purchase_id,
    pu.purchase_date,
    pu.supplier_name,
    l.location_name,
    COUNT(pi.item_id)                        AS total_items,
    SUM(pi.quantity)                         AS total_units,
    SUM(pi.quantity * pi.purchase_price_etb) AS total_cost_etb
FROM purchases pu
JOIN purchase_items pi ON pu.purchase_id = pi.purchase_id
JOIN locations l       ON pu.location_id = l.location_id
WHERE pu.purchase_id = (SELECT MAX(purchase_id)
                        FROM purchases
                        WHERE supplier_name != 'Opening Stock')
GROUP BY pu.purchase_id, pu.purchase_date,
         pu.supplier_name, l.location_name;
