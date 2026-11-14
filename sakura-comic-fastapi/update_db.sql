-- 为 sakura_user 表添加新字段

-- 添加 is_admin 字段
ALTER TABLE sakura_user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE AFTER password_hash;

-- 添加 created_at 字段
ALTER TABLE sakura_user ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP AFTER is_admin;

-- 查看表结构
DESC sakura_user;
