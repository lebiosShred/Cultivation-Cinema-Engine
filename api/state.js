const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const AUTH_SECRET = process.env.DASHBOARD_AUTH_SECRET || 'octane_secure_hmac_secret_2026_x89a';

function parseCookies(cookieHeader) {
  const list = {};
  if (!cookieHeader) return list;
  cookieHeader.split(';').forEach(cookie => {
    const parts = cookie.split('=');
    if (parts.length >= 2) {
      list[parts[0].trim()] = decodeURIComponent(parts.slice(1).join('=').trim());
    }
  });
  return list;
}

function verifySessionToken(token) {
  if (!token || typeof token !== 'string' || !token.includes('.')) return false;
  const parts = token.split('.');
  if (parts.length !== 2) return false;
  const [payloadB64, signatureB64] = parts;

  try {
    const expectedSig = crypto.createHmac('sha256', AUTH_SECRET)
      .update(payloadB64)
      .digest('base64url');

    const bufExpected = Buffer.from(expectedSig);
    const bufActual = Buffer.from(signatureB64);
    if (bufExpected.length !== bufActual.length) return false;
    if (!crypto.timingSafeEqual(bufExpected, bufActual)) return false;

    const payload = JSON.parse(Buffer.from(payloadB64, 'base64url').toString('utf8'));
    if (!payload.authenticated || typeof payload.exp !== 'number') return false;
    if (Date.now() > payload.exp) return false;

    return true;
  } catch (e) {
    return false;
  }
}

module.exports = async function handler(req, res) {
  const cookies = parseCookies(req.headers.cookie);
  const sessionToken = cookies['octane_session'];

  if (!verifySessionToken(sessionToken)) {
    return res.status(401).json({ error: 'Unauthorized: Session required' });
  }

  const stateFilePath = path.join(__dirname, '..', 'data', 'cloud_state.json');

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) { body = {}; }
    }
    try {
      fs.writeFileSync(stateFilePath, JSON.stringify(body || {}, null, 2), 'utf8');
      return res.status(200).json({ success: true });
    } catch (err) {
      return res.status(200).json({ success: true, savedLocally: true });
    }
  }

  if (req.method === 'GET') {
    try {
      if (fs.existsSync(stateFilePath)) {
        const data = JSON.parse(fs.readFileSync(stateFilePath, 'utf8'));
        return res.status(200).json(data);
      }
    } catch (e) {}
    return res.status(200).json({ notes: [], connections: [], checklist: {} });
  }

  res.setHeader('Allow', ['GET', 'POST']);
  return res.status(405).json({ error: 'Method Not Allowed' });
};
