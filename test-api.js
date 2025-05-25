const https = require('https');

const data = JSON.stringify({
  email: 'test123@example.com',
  password: 'test123',
  name: 'Test User'
});

const options = {
  hostname: 'frizerie.onrender.com',
  port: 443,
  path: '/api/v1/users/register',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length,
    'Origin': 'https://frizerie-frontend.vercel.app'
  }
};

const req = https.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);
  
  res.on('data', (chunk) => {
    console.log(`Response: ${chunk}`);
  });
});

req.on('error', (e) => {
  console.error(`Error: ${e.message}`);
});

req.write(data);
req.end(); 