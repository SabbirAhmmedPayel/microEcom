const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD, // Ensure this matches your pgAdmin password
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    port: 5432,
});

module.exports = pool;