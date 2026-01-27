const pool = require('./db');

pool.query('SELECT NOW()', (err, res) => {
    if (err) {
        console.error('Connection error', err.stack);
    } else {
        console.log('Database connected at:', res.rows[0].now);
    }
    process.exit();
});