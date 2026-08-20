-- ============================================================
-- FILE: 03_seed_data.sql
-- PROJECT: Nate Data — Small Business Intelligence System
-- AUTHOR: Natnael Haile
-- PURPOSE: Insert initial reference data (locations, categories,
--          owner user). Product inventory imported via Python.
-- ============================================================
-- NOTE: Uses INSERT IGNORE to safely skip rows that already exist
-- ============================================================

USE nate_data;

-- ------------------------------------------------------------
-- LOCATIONS (3 physical locations)
-- ------------------------------------------------------------
INSERT IGNORE INTO locations (location_id, location_name, location_type, city) VALUES
    (1, 'Shop 1',    'shop',      'Dessie'),
    (2, 'Shop 2',    'shop',      'Dessie'),
    (3, 'Warehouse', 'warehouse', 'Dessie');

-- ------------------------------------------------------------
-- CATEGORIES (13 product categories from real inventory)
-- ------------------------------------------------------------
INSERT IGNORE INTO categories (category_id, category_name) VALUES
    (1,  'Breaker'),
    (2,  'Electrical Component'),
    (3,  'Grand'),
    (4,  'Haud'),
    (5,  'Lamp'),
    (6,  'Magnetic Light'),
    (7,  'Mirror Light'),
    (8,  'Panel Light'),
    (9,  'Pawza'),
    (10, 'Plastic Globe'),
    (11, 'Spot Light'),
    (12, 'Strip Light'),
    (13, 'Vegas');

-- ------------------------------------------------------------
-- OWNER USER
-- Natnael is the owner with full access
-- location_id NULL means the owner is not assigned to one shop
-- ------------------------------------------------------------
INSERT IGNORE INTO users (user_id, full_name, role, location_id) VALUES
    (1, 'Natnael Haile', 'owner', NULL);
-- Test query to verify connection
SELECT * FROM locations;
