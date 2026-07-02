-- ============================================
-- Personal Finance Tracker - Database Init
-- ============================================

CREATE DATABASE IF NOT EXISTS finance_tracker
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE finance_tracker;

-- ============================================
-- Users table
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- Categories table
-- ============================================
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',
    icon VARCHAR(50) DEFAULT '📌',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_category (user_id, name, type)
) ENGINE=InnoDB;

-- ============================================
-- Transactions table
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    description TEXT,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================
-- Budgets table
-- ============================================
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE KEY unique_budget (user_id, category_id, month, year)
) ENGINE=InnoDB;

-- ============================================
-- Default categories (for new users)
-- ============================================
-- These are inserted programmatically via the app,
-- but you can run them here as seed data if needed:

-- Income categories
-- INSERT INTO categories (user_id, name, type, color, icon, is_default) VALUES
-- (1, 'Lương', 'income', '#10B981', '💰', TRUE),
-- (1, 'Thưởng', 'income', '#34D399', '🎁', TRUE),
-- (1, 'Đầu tư', 'income', '#6EE7B7', '📈', TRUE),
-- (1, 'Thu nhập phụ', 'income', '#A7F3D0', '💼', TRUE);

-- Expense categories
-- INSERT INTO categories (user_id, name, type, color, icon, is_default) VALUES
-- (1, 'Ăn uống', 'expense', '#EF4444', '🍔', TRUE),
-- (1, 'Di chuyển', 'expense', '#F87171', '🚗', TRUE),
-- (1, 'Nhà ở', 'expense', '#FCA5A5', '🏠', TRUE),
-- (1, 'Giải trí', 'expense', '#FEE2E2', '🎮', TRUE),
-- (1, 'Mua sắm', 'expense', '#DC2626', '🛍️', TRUE),
-- (1, 'Sức khỏe', 'expense', '#B91C1C', '💊', TRUE),
-- (1, 'Học tập', 'expense', '#991B1B', '📚', TRUE),
-- (1, 'Hóa đơn', 'expense', '#7F1D1D', '🧾', TRUE);
