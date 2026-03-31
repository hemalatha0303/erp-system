-- SQL Script to Add Admin User to Railway Database
-- Run this in Railway MySQL Console or via any MySQL client

-- Add Admin User
-- This creates an admin with email: admin@vvit.net, password: Admin@123

INSERT INTO users (email, password, role, is_active)
VALUES (
    'admin@vvit.net',
    '$argon2id$v=19$m=65536,t=3,p=4$JuQc47x3bk0pRaiV8t5bCw$GfiaKoe1xOmZPVqFVDnAmt7lcdCbn/Dfoh4iaUDURwM',  -- argon2 hash of "Admin@123"
    'ADMIN',
    1
);

-- Create Admin Profile
INSERT INTO admin_profiles (email, name, mobile_no, designation)
VALUES (
    'admin@vvit.net',
    'System Admin',
    '',
    ''
);

-- Verify admin was created
SELECT * FROM users WHERE email = 'admin@vvit.net';
SELECT * FROM admin_profiles WHERE email = 'admin@vvit.net';
