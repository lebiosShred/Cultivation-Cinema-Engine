// Local Node.js Development Server (Replicating Vercel Edge Middleware & Serverless APIs)
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = process.env.PORT || 3000;
const AUTH_SECRET = process.env.DASHBOARD_AUTH_SECRET || 'octane_secure_hmac_secret_2026_x89a';
const CORRECT_PASSWORD = process.env.DASHBOARD_PASSWORD || 'OctaneOnly2026';

function verifySessionToken(token) {
  if (!token || typeof token !== 'string' || !token.includes('.')) return false;
  const [payloadB64, signatureB64] = token.split('.');
  
  const expectedSig = crypto.createHmac('sha256', AUTH_SECRET)
    .update(payloadB64)
    .digest('base64url');

  if (signatureB64 !== expectedSig) return false;

  try {
    const payload = JSON.parse(Buffer.from(payloadB64, 'base64url').toString('utf8'));
    if (!payload.authenticated || typeof payload.exp !== 'number') return false;
    if (Date.now() > payload.exp) return false;
    return true;
  } catch (e) {
    return false;
  }
}

function parseCookies(req) {
  const list = {};
  const rc = req.headers.cookie;
  if (!rc) return list;
  rc.split(';').forEach(cookie => {
    const parts = cookie.split('=');
    list[parts.shift().trim()] = decodeURI(parts.join('='));
  });
  return list;
}

const server = http.createServer(async (req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
  const pathname = parsedUrl.pathname;

  // 1. Auth Endpoint: POST /api/auth
  if (pathname === '/api/auth' && req.method === 'POST') {
    let bodyStr = '';
    req.on('data', chunk => bodyStr += chunk);
    req.on('end', async () => {
      let body = {};
      try { body = JSON.parse(bodyStr); } catch (e) {}

      const password = body.password || '';
      const bufA = Buffer.from(String(password));
      const bufB = Buffer.from(String(CORRECT_PASSWORD));
      const isMatch = bufA.length === bufB.length && crypto.timingSafeEqual(bufA, bufB);

      if (!isMatch) {
        await new Promise(r => setTimeout(r, 400));
        res.writeHead(401, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ success: false, error: 'Invalid access key. Access denied.' }));
      }

      const payload = Buffer.from(JSON.stringify({
        authenticated: true,
        exp: Date.now() + 24 * 60 * 60 * 1000
      })).toString('base64url');

      const signature = crypto.createHmac('sha256', AUTH_SECRET).update(payload).digest('base64url');
      const token = `${payload}.${signature}`;

      res.writeHead(200, {
        'Content-Type': 'application/json',
        'Set-Cookie': `octane_session=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400`
      });
      return res.end(JSON.stringify({ success: true, redirect: '/' }));
    });
    return;
  }

  // 2. Logout Endpoint: /api/logout
  if (pathname === '/api/logout') {
    res.writeHead(302, {
      'Location': '/login',
      'Set-Cookie': 'octane_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'
    });
    return res.end();
  }

  // 2.5 Leads Endpoint: GET /api/leads (Authenticated)
  if (pathname === '/api/leads') {
    const leadsHandler = require('./api/leads.js');
    req.query = Object.fromEntries(parsedUrl.searchParams);
    return leadsHandler(req, {
      setHeader: (k, v) => res.setHeader(k, v),
      status: (code) => ({
        json: (data) => {
          res.writeHead(code, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(data));
        }
      })
    });
  }

  // 2.6 Realtime Endpoint: GET /api/realtime
  if (pathname === '/api/realtime') {
    const handler = require('./api/realtime.js');
    req.query = Object.fromEntries(parsedUrl.searchParams);
    return handler(req, {
      setHeader: (k, v) => res.setHeader(k, v),
      status: (code) => ({
        json: (data) => {
          res.writeHead(code, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(data));
        }
      })
    });
  }

  // 2.7 State Persistence Endpoint: /api/state
  if (pathname === '/api/state') {
    const handler = require('./api/state.js');
    req.query = Object.fromEntries(parsedUrl.searchParams);
    if (req.method === 'POST') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        req.body = body;
        return handler(req, {
          setHeader: (k, v) => res.setHeader(k, v),
          status: (code) => ({
            json: (data) => {
              res.writeHead(code, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify(data));
            }
          })
        });
      });
      return;
    }
    return handler(req, {
      setHeader: (k, v) => res.setHeader(k, v),
      status: (code) => ({
        json: (data) => {
          res.writeHead(code, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(data));
        }
      })
    });
  }

  // 2.8 Telemetry Endpoint: /api/telemetry
  if (pathname === '/api/telemetry') {
    const handler = require('./api/telemetry.js');
    req.query = Object.fromEntries(parsedUrl.searchParams);
    return handler(req, {
      setHeader: (k, v) => res.setHeader(k, v),
      status: (code) => ({
        json: (data) => {
          res.writeHead(code, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(data));
        }
      })
    });
  }

  // 2.9 Blog Stats Endpoint: /api/get-blog-stats
  if (pathname === '/api/get-blog-stats') {
    const handler = require('./api/get-blog-stats.js');
    req.query = Object.fromEntries(parsedUrl.searchParams);
    return handler(req, {
      setHeader: (k, v) => res.setHeader(k, v),
      status: (code) => ({
        json: (data) => {
          res.writeHead(code, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(data));
        }
      })
    });
  }

  // 3. Login Page Route
  if (pathname === '/login' || pathname === '/login.html') {
    const filePath = path.join(__dirname, 'login.html');
    if (fs.existsSync(filePath)) {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return fs.createReadStream(filePath).pipe(res);
    }
  }

  // 4. Public Assets Whitelist
  if (
    pathname.endsWith('.ico') ||
    pathname.endsWith('.png') ||
    pathname.endsWith('.jpg') ||
    pathname.endsWith('.svg')
  ) {
    const filePath = path.join(__dirname, pathname.replace(/^\//, ''));
    if (fs.existsSync(filePath)) {
      const ext = path.extname(filePath).toLowerCase();
      const mime = ext === '.png' ? 'image/png' : ext === '.svg' ? 'image/svg+xml' : 'image/x-icon';
      res.writeHead(200, { 'Content-Type': mime });
      return fs.createReadStream(filePath).pipe(res);
    }
  }

  // 5. Edge Middleware Check (Gating)
  const cookies = parseCookies(req);
  const token = cookies['octane_session'];
  const isAuthenticated = verifySessionToken(token);

  if (!isAuthenticated) {
    if (pathname.startsWith('/api/')) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ error: 'Unauthorized: Valid session required' }));
    }
    // Redirect all unauthenticated page and JS requests to /login
    res.writeHead(302, { 'Location': '/login' });
    return res.end();
  }

  // 6. Authenticated Requests: Serve Application Assets
  let targetFile = pathname === '/' ? 'dashboard_enterprise.html' : pathname.replace(/^\//, '');
  const filePath = path.join(__dirname, targetFile);

  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    const ext = path.extname(filePath).toLowerCase();
    let mime = 'text/plain';
    if (ext === '.html') mime = 'text/html; charset=utf-8';
    else if (ext === '.css') mime = 'text/css; charset=utf-8';
    else if (ext === '.js') mime = 'application/javascript; charset=utf-8';
    else if (ext === '.json') mime = 'application/json; charset=utf-8';

    res.writeHead(200, { 'Content-Type': mime });
    return fs.createReadStream(filePath).pipe(res);
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not Found');
});

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`🔒 Octane Gated Dashboard server running at http://localhost:${PORT}`);
    console.log(`Protected by Edge Middleware with password: "${CORRECT_PASSWORD}"`);
  });
}

module.exports = server;
