-- SQL Script to Add Admin User to Railway Database
-- Run this in Railway MySQL Console or via any MySQL client

-- First, get the next available user ID
SELECT MAX(id) + 1 as next_id FROM user;

-- Add Admin User (adjust ID based on result above, usually starts at 1)
-- This creates an admin with email: admin@vvit.net, password: Admin@123

INSERT INTO user (email, password_hash, role, is_active, created_at, updated_at)
VALUES (
    'admin@vvit.net',
    '$2b$12$slYQmyNdGzyLp4LCwC5rM.EJ.9z.qrqOy5z5NM5K0QQ.0GNcj3iOC',  -- bcrypt hash of "Admin@123"
    'ADMIN',
    1,
    NOW(),
    NOW()
);

-- Get the newly created user ID
SET @admin_user_id = LAST_INSERT_ID();

-- Create Admin Profile
INSERT INTO admin_profile (uid, first_name, last_name, email, personal_email, mobile_no, address, qualification, experience, department, created_at, updated_at)
VALUES (
    @admin_user_id,
    'System',
    'Admin',
    'admin@vvit.net',
    'admin@vvit.net',
    '',
    '',
    '',
    '',
    '',
    NOW(),
    NOW()
);

-- Verify admin was created
SELECT * FROM user WHERE email = 'admin@vvit.net';
SELECT * FROM admin_profile WHERE email = 'admin@vvit.net';
