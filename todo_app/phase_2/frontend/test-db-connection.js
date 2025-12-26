const { Pool } = require('pg');

const pool = new Pool({
  connectionString: "postgresql://neondb_owner:npg_SQx9TYhswN6G@ep-summer-forest-a4cxd4k1-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require",
  ssl: {
    rejectUnauthorized: false,
  },
  connectionTimeoutMillis: 15000,
});

console.log('Testing connection...');
const start = Date.now();

pool.query('SELECT NOW()', (err, res) => {
  const elapsed = Date.now() - start;
  if (err) {
    console.error('❌ Error:');
    console.error(JSON.stringify(err, null, 2));
    console.error('Stack:', err.stack);
    console.error('Time taken:', elapsed + 'ms');
  } else {
    console.log('✅ Connected successfully!');
    console.log('Time taken:', elapsed + 'ms');
    console.log('Result:', res.rows[0]);
  }
  pool.end();
});
