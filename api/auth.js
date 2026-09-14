const crypto = require('crypto');

const AUTH_SECRET = process.env.DASHBOARD_AUTH_SECRET || 'octane_secure_hmac_secret_2026_x89a';
const CORRECT_PASSWORD = process.env.DASHBOARD_PASSWORD || 'OctaneOnly2026';

function safeCompare(a, b) {
  try {
    const bufA = Buffer.from(String(a));
    const bufB = Buffer.from(String(b));
    if (bufA.length !== bufB.length) {
      // Compare against dummy to keep constant time
      crypto.timingSafeEqual(bufA, bufA);
      return false;
    }
    return crypto.timingSafeEqual(bufA, bufB);
  } catch (e) {
    return false;
  }
}

function createSessionToken() {
  const payload = Buffer.from(JSON.stringify({
    authenticated: true,
    exp: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
  })).toString('base64url');
  
  const signature = crypto.createHmac('sha256', AUTH_SECRET)
    .update(payload)
    .digest('base64url');
    
  return `${payload}.${signature}`;
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body);
    } catch (e) {
      body = {};
    }
  }

  const password = body ? body.password : '';

  if (!password || !safeCompare(password, CORRECT_PASSWORD)) {
    // Artificial 400ms delay to thwart automated brute-force timing attacks
    await new Promise(resolve => setTimeout(resolve, 400));
    return res.status(401).json({
      success: false,
      error: 'Invalid access key. Access denied.'
    });
  }

  const token = createSessionToken();
  const isHttps = req.headers['x-forwarded-proto'] === 'https' || 
                  (req.headers.host && req.headers.host.includes('vercel.app'));
  
  const secureFlag = isHttps ? 'Secure; ' : '';
  const cookieHeader = `octane_session=${token}; Path=/; HttpOnly; ${secureFlag}SameSite=Strict; Max-Age=86400`;

  res.setHeader('Set-Cookie', cookieHeader);
  return res.status(200).json({
    success: true,
    redirect: '/'
  });
};
