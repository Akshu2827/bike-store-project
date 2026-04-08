-- =============================================
-- BIKE STORE DATABASE - INIT SCRIPT (Fully Rerunnable + Fixed)
-- =============================================

-- Drop tables safely (rerunnable)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS stocks CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS staffs CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
DROP TABLE IF EXISTS brands CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

-- =============================================
-- CREATE TABLES
-- =============================================

CREATE TABLE brands (
    brand_id INT PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL
);

CREATE TABLE categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone VARCHAR(25),
    email VARCHAR(255),
    street VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10)
);

CREATE TABLE stores (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL,
    phone VARCHAR(25),
    email VARCHAR(255),
    street VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10)
);

CREATE TABLE staffs (
    staff_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(25),
    active SMALLINT NOT NULL DEFAULT 1,
    store_id INT NOT NULL,
    manager_id INT,
    CONSTRAINT fk_staff_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
    CONSTRAINT fk_staff_manager FOREIGN KEY (manager_id) REFERENCES staffs(staff_id)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    brand_id INT NOT NULL,
    category_id INT NOT NULL,
    model_year SMALLINT NOT NULL,
    list_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE stocks (
    store_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    PRIMARY KEY (store_id, product_id),
    CONSTRAINT fk_stock_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
    CONSTRAINT fk_stock_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_status SMALLINT NOT NULL,
    order_date DATE NOT NULL,
    required_date DATE NOT NULL,
    shipped_date DATE,
    store_id INT NOT NULL,
    staff_id INT NOT NULL,
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_order_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
    CONSTRAINT fk_order_staff FOREIGN KEY (staff_id) REFERENCES staffs(staff_id)
);

CREATE TABLE order_items (
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    list_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (order_id, item_id),
    CONSTRAINT fk_orderitem_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_orderitem_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- =============================================
-- LOAD DATA
-- =============================================

COPY brands(brand_id, brand_name) 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/brands.csv' 
DELIMITER ',' CSV HEADER;

COPY categories(category_id, category_name) 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/categories.csv' 
DELIMITER ',' CSV HEADER;

COPY customers 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/customers.csv' 
DELIMITER ',' CSV HEADER;

COPY stores 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/stores.csv' 
DELIMITER ',' CSV HEADER;

-- Staffs: Self-referencing FK
ALTER TABLE staffs DISABLE TRIGGER ALL;

COPY staffs 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/staffs.csv' 
DELIMITER ',' CSV HEADER;

ALTER TABLE staffs ENABLE TRIGGER ALL;

COPY products 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/products.csv' 
DELIMITER ',' CSV HEADER;

COPY stocks 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/stocks.csv' 
DELIMITER ',' CSV HEADER;

-- FIXED: Orders - Convert '0' in shipped_date to NULL
COPY orders 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/orders.csv' 
DELIMITER ',' CSV HEADER NULL '0';

-- Order Items (now safe)
COPY order_items 
FROM 'E:/Mostly_everything_related_to_coding_DS/business_case_studies/bike-store-project/bike-store-project/data/order_items.csv' 
DELIMITER ',' CSV HEADER;

-- =============================================
-- CREATE VIEW + INDEXES
-- =============================================

CREATE OR REPLACE VIEW sales_summary AS
SELECT 
    o.order_id,
    o.order_date,
    o.order_status,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.city, c.state,
    p.product_name,
    b.brand_name,
    cat.category_name,
    oi.quantity,
    oi.list_price,
    oi.discount,
    ROUND(oi.quantity * oi.list_price * (1 - oi.discount), 2) AS revenue,
    s.store_name,
    CONCAT(st.first_name, ' ', st.last_name) AS staff_name,
    o.shipped_date
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN brands b ON p.brand_id = b.brand_id
JOIN categories cat ON p.category_id = cat.category_id
JOIN stores s ON o.store_id = s.store_id
JOIN staffs st ON o.staff_id = st.staff_id;

CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);

-- =============================================
-- VERIFY
-- =============================================

SELECT 'Brands' AS table_name, COUNT(*) AS row_count FROM brands
UNION ALL SELECT 'Categories', COUNT(*) FROM categories
UNION ALL SELECT 'Stores', COUNT(*) FROM stores
UNION ALL SELECT 'Staffs', COUNT(*) FROM staffs
UNION ALL SELECT 'Customers', COUNT(*) FROM customers
UNION ALL SELECT 'Products', COUNT(*) FROM products
UNION ALL SELECT 'Stocks', COUNT(*) FROM stocks
UNION ALL SELECT 'Orders', COUNT(*) FROM orders
UNION ALL SELECT 'Order Items', COUNT(*) FROM order_items;

-- Check how many orders have shipped_date as NULL (previously '0')
SELECT COUNT(*) AS unshipped_orders FROM orders WHERE shipped_date IS NULL;


-- 1. Total revenue
SELECT ROUND(SUM(quantity * list_price * (1 - discount)), 2) AS total_revenue
FROM order_items;

-- 2. Sales by store
SELECT s.store_name, 
       COUNT(DISTINCT o.order_id) AS total_orders,
       ROUND(SUM(oi.quantity * oi.list_price * (1 - oi.discount)), 2) AS revenue
FROM orders o
JOIN stores s ON o.store_id = s.store_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY s.store_name
ORDER BY revenue DESC;

-- 3. Top 10 best-selling products
SELECT p.product_name, b.brand_name, 
       SUM(oi.quantity) AS units_sold,
       ROUND(SUM(oi.quantity * oi.list_price * (1 - oi.discount)), 2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN brands b ON p.brand_id = b.brand_id
GROUP BY p.product_name, b.brand_name
ORDER BY units_sold DESC
LIMIT 10;

-- 4. See the sales_summary view (combines everything nicely)
SELECT * FROM sales_summary 
ORDER BY order_date DESC 
LIMIT 20;