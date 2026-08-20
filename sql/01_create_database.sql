-- ============================================================
-- FILE: 01_create_database.sql
-- PROJECT: Nate Data — Small Business Intelligence System
-- AUTHOR: Natnael Haile
-- PURPOSE: Create the nate_data database
-- ============================================================
-- HOW TO RUN:
--   mysql -u root -p < 01_create_database.sql
-- OR copy and paste into mysql> terminal
-- ============================================================

-- Create the database if it does not already exist
-- IF NOT EXISTS means: do not throw an error if it already exists
CREATE DATABASE IF NOT EXISTS nate_data;

-- Select it as the active database
USE nate_data;
