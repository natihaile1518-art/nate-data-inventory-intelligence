# Nate Data — SQL Source Files

This folder contains all SQL source code for the nate_data MySQL database.
These files are the complete history of the database schema and seed data.

## File Structure

| File | Purpose |
|------|---------|
| `01_create_database.sql` | Creates the nate_data database |
| `02_create_tables.sql` | Creates all 10 tables in dependency order |
| `03_seed_data.sql` | Inserts reference data (locations, categories, owner) |

## How to Run

### Run a single file
```
mysql -u root -p nate_data < 02_create_tables.sql
```

### Run from inside mysql> prompt
```sql
SOURCE C:/Users/DELL/Documents/Summer_Projects/sql/02_create_tables.sql
```

## Table Dependency Order

```
locations      (no dependencies)
categories     (no dependencies)
products       → categories
users          → locations
inventory_snapshots → products, locations
purchases      → locations, users
purchase_items → purchases, products
sales          → locations, users
sale_items     → sales, products
inventory_adjustments → products, locations, users
```

## Important Notes

- Products are imported via Python script, not SQL seed file
- Warehouse data is SIMULATED / DEMO DATA — clearly labeled
- Never delete products with transaction history — use is_active = 0
- Purchase prices live in purchase_items, not products
- Current inventory is always CALCULATED, never manually stored
