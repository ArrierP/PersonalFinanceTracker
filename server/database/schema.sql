CREATE DATABASE if not EXISTS personal_finance_db
CHARACTER set utf8mb4 COLLATE utf8mb4_unicode_ci;

Use personal_finance_db;


create table if not exists users (
    id int auto_increment PRIMARY key,
    email VARCHAR(255) not NULL UNIQUE,
    password VARCHAR(20) not null,
    full_name VARCHAR(50) not null,
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp on update current_timestamp
);

alter table users auto_increment = 2000;

create table if not exists categories (
    id int auto_increment PRIMARY key,
    user_id int NULL,
    name VARCHAR(100) not NULL,
    type Enum('INCOME', 'EXPENSE') not NULL,
    icon VARCHAR(100) null,
    created_at TIMESTAMP DEFAULT current_timestamp,
    FOREIGN KEY (user_id) REFERENCES users(id) on delete CASCADE,
    UNIQUE KEY uq_cate_user_name_type (user_id, name, type)
);

create Table if not exists transactions (
    id int PRIMARY KEY auto_increment,
    user_id int not null,
    category_id int not null,
    amount DECIMAL(10, 2) NOT NULL,
    type ENUM('INCOME', 'EXPENSE') not NULL,
    transaction_date DATE not NULL,
    note TEXT NULL,
    payment_method VARCHAR(50) DEFAULT 'BANK_TRANSFER',
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp on update current_timestamp,
    FOREIGN KEY (user_id) REFERENCES users(id) on delete CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) on delete set null,
    index idx_tx_user_date (user_id, transaction_date),
    index idx_tx_user_cat (user_id, category_id),
    index idx_tx_type (type)
);

CREATE Table if not exists budgets (
    id int auto_increment PRIMARY KEY,
    user_id int not NULL,
    category_id int NULL,
    amount_limit DECIMAL(15, 2) not NULL,
    month int not null,
    year int not null,
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp on update current_timestamp,
    FOREIGN KEY (user_id) REFERENCES users(id) on delete CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) on delete cascade,
    UNIQUE key uq_budget_user_cat_period (user_id, category_id, month, year)
);

CREATE TABLE IF NOT EXISTS financial_snapshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    record_date DATE NOT NULL,
    monthly_income DECIMAL(15, 2) NOT NULL,
    monthly_expense_total DECIMAL(15, 2) NOT NULL,
    actual_savings DECIMAL(15, 2) NOT NULL,
    savings_rate DECIMAL(5, 4) NOT NULL,
    essential_spending DECIMAL(15, 2) NOT NULL,
    discretionary_spending DECIMAL(15, 2) NOT NULL,
    credit_score FLOAT NULL,
    debt_to_income_ratio FLOAT NULL,
    emergency_fund DECIMAL(15, 2) NULL,
    financial_scenario VARCHAR(50) NULL,
    cash_flow_status VARCHAR(50) NULL,
    financial_stress_level VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_snap_user_date (user_id, record_date)
);

create Table if not exists refresh_token (
    id int auto_increment PRIMARY key,
    user_id int not null,
    token_hash VARCHAR(64) not NULL UNIQUE,
    expires_at DATE not null,
    revoked TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT current_timestamp,
    Foreign Key (userid) REFERENCES users(id) on delete CASCADE,
    index idx_rt_user_id (user_id),
    index idx_rt_expires_at (expires_at) 
)

INSERT IGNORE INTO categories (user_id, name, type, icon) VALUES
-- 10 Expense Categories
(NULL, 'Rent', 'EXPENSE', 'home'),
(NULL, 'Groceries', 'EXPENSE', 'shopping-cart'),
(NULL, 'Dining Out', 'EXPENSE', 'utensils'),
(NULL, 'Utilities', 'EXPENSE', 'zap'),
(NULL, 'Transportation', 'EXPENSE', 'car'),
(NULL, 'Healthcare', 'EXPENSE', 'heart-pulse'),
(NULL, 'Education', 'EXPENSE', 'graduation-cap'),
(NULL, 'Entertainment', 'EXPENSE', 'film'),
(NULL, 'Insurance', 'EXPENSE', 'shield'),
(NULL, 'Investments', 'EXPENSE', 'trending-up'),
-- 3 Income Categories
(NULL, 'Salary', 'INCOME', 'briefcase'),
(NULL, 'Freelance', 'INCOME', 'laptop'),
(NULL, 'Mixed', 'INCOME', 'wallet');


