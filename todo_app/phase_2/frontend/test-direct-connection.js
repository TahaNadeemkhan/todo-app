const { Pool } = require('pg');

// Try direct endpoint instead of pooler
const pool = new Pool({
  connectionString: "postgresql://neondb_owner:npg_SQx9TYhswN6G@ep-summer-forest-a4cxd4k1.us-east-1.aws.neon.tech/neondb?sslmode=require",
  ssl: {
    rejectUnauthorized: false,
  },
  connectionTimeoutMillis: 15000,
});

console.log('Testing DIRECT connection (non-pooler)...');
const start = Date.now();

pool.query('SELECT NOW()', (err, res) => {
  const elapsed = Date.now() - start;
  if (err) {
    console.error('❌ Error:', err.code, err.message);
    console.error('Time taken:', elapsed + 'ms');
  } else {
    console.log('✅ Connected successfully!');
    console.log('Time taken:', elapsed + 'ms');
    console.log('Result:', res.rows[0]);
  }
  pool.end();
});
