-- ============================================================
-- FILE: 02_create_tables.sql
-- PROJECT: Nate Data — Small Business Intelligence System
-- AUTHOR: Natnael Haile
-- PURPOSE: Create all tables in the correct dependency order
-- ============================================================
-- DEPENDENCY ORDER (create tables in this order):
--   1. locations      (depends on nothing)
--   2. categories     (depends on nothing)
--   3. products       (depends on categories)
--   4. users          (depends on locations)
--   5. inventory_snapshots (depends on products + locations)
--   6. purchases      (depends on locations + users)
--   7. purchase_items (depends on purchases + products)
--   8. sales          (depends on locations + users)
--   9. sale_items     (depends on sales + products)
--  10. inventory_adjustments (depends on products + locations + users)
-- ============================================================
-- HOW TO RUN:
--   mysql -u root -p nate_data < 02_create_tables.sql
-- ============================================================

USE nate_data;

-- ------------------------------------------------------------
-- TABLE 1: locations
-- Stores the physical locations of the business:
-- Shop 1, Shop 2, and Warehouse
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS locations (
    location_id   INT          NOT NULL AUTO_INCREMENT,
    location_name VARCHAR(100) NOT NULL,
    location_type VARCHAR(20)  NOT NULL DEFAULT 'shop',
    city          VARCHAR(100) NOT NULL DEFAULT 'Dessie',
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (location_id)
);

-- ------------------------------------------------------------
-- TABLE 2: categories
-- Stores the 13 product categories
-- UNIQUE KEY prevents duplicate category names
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id   INT         NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    is_active     TINYINT(1)  NOT NULL DEFAULT 1,
    PRIMARY KEY (category_id),
    UNIQUE KEY uq_category_name (category_name)
);

-- ------------------------------------------------------------
-- TABLE 3: products
-- Stores the permanent identity of every product
-- References categories via foreign key
-- specification allows NULL (some products have no spec)
-- is_active = 0 means discontinued (soft delete)
-- created_at is filled automatically by MySQL
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id    VARCHAR(10)  NOT NULL,
    product_name  VARCHAR(100) NOT NULL,
    category_id   INT          NOT NULL,
    specification VARCHAR(50)  NULL,
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- ------------------------------------------------------------
-- TABLE 4: users
-- Stores workers and the owner
-- shop_id references locations — the worker's current assignment
-- role: 'owner' or 'staff'
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id    INT          NOT NULL AUTO_INCREMENT,
    full_name  VARCHAR(100) NOT NULL,
    role       VARCHAR(20)  NOT NULL DEFAULT 'staff',
    location_id INT         NULL,
    is_active  TINYINT(1)   NOT NULL DEFAULT 1,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- ------------------------------------------------------------
-- TABLE 5: inventory_snapshots
-- Stores physical inventory counts on a specific date
-- This is where the existing Excel inventory data goes
-- It becomes the starting point for all stock calculations
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory_snapshots (
    snapshot_id  INT        NOT NULL AUTO_INCREMENT,
    product_id   VARCHAR(10) NOT NULL,
    location_id  INT        NOT NULL,
    quantity     INT        NOT NULL DEFAULT 0,
    count_date   DATE       NOT NULL,
    notes        VARCHAR(255) NULL,
    created_at   TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (snapshot_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- ------------------------------------------------------------
-- TABLE 6: purchases
-- Header table for purchase transactions
-- One row per purchase event (delivery from supplier)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchases (
    purchase_id   INT          NOT NULL AUTO_INCREMENT,
    location_id   INT          NOT NULL,
    user_id       INT          NOT NULL,
    purchase_date DATE         NOT NULL,
    supplier_name VARCHAR(100) NULL,
    notes         VARCHAR(255) NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (purchase_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (user_id)     REFERENCES users(user_id)
);

-- ------------------------------------------------------------
-- TABLE 7: purchase_items
-- Detail table for purchase transactions
-- One row per product line within a purchase
-- purchase_price_etb stored here — preserves price history
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchase_items (
    item_id           INT            NOT NULL AUTO_INCREMENT,
    purchase_id       INT            NOT NULL,
    product_id        VARCHAR(10)    NOT NULL,
    quantity          INT            NOT NULL,
    purchase_price_etb DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (item_id),
    FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);

-- ------------------------------------------------------------
-- TABLE 8: sales
-- Header table for sales transactions
-- One row per customer transaction
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales (
    sale_id    INT       NOT NULL AUTO_INCREMENT,
    location_id INT      NOT NULL,
    user_id    INT       NOT NULL,
    sale_date  DATE      NOT NULL,
    notes      VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sale_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (user_id)     REFERENCES users(user_id)
);

-- ------------------------------------------------------------
-- TABLE 9: sale_items
-- Detail table for sales transactions
-- One row per product line within a sale
-- selling_price_etb stored here — different from purchase price
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sale_items (
    item_id          INT            NOT NULL AUTO_INCREMENT,
    sale_id          INT            NOT NULL,
    product_id       VARCHAR(10)    NOT NULL,
    quantity_sold    INT            NOT NULL,
    selling_price_etb DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (item_id),
    FOREIGN KEY (sale_id)    REFERENCES sales(sale_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ------------------------------------------------------------
-- TABLE 10: inventory_adjustments
-- Handles all stock changes outside of sales and purchases:
-- damaged, lost, transfer between locations, corrections
-- quantity is positive (stock added) or negative (stock removed)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory_adjustments (
    adjustment_id INT            NOT NULL AUTO_INCREMENT,
    product_id    VARCHAR(10)    NOT NULL,
    location_id   INT            NOT NULL,
    user_id       INT            NOT NULL,
    quantity      INT            NOT NULL,
    reason        VARCHAR(50)    NOT NULL,
    notes         VARCHAR(255)   NULL,
    adjustment_date DATE         NOT NULL,
    created_at    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (adjustment_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (user_id)     REFERENCES users(user_id)
);
