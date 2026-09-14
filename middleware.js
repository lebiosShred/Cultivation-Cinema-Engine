// Vercel Edge Middleware — Zero-Leak Security Gate
// Enforces that unauthenticated clients NEVER receive dashboard JS, HTML, or API telemetry.

const AUTH_SECRET = process.env.DASHBOARD_AUTH_SECRET || 'octane_secure_hmac_secret_2026_x89a';

function base64urlToBytes(b64url) {
  let b64 = b64url.replace(/-/g, '+').replace(/_/g, '/');
  while (b64.length % 4) b64 += '=';
  const binStr = atob(b64);
  const bytes = new Uint8Array(binStr.length);
  for (let i = 0; i < binStr.length; i++) bytes[i] = binStr.charCodeAt(i);
  return bytes;
}

async function verifySessionToken(token) {
  if (!token || typeof token !== 'string' || !token.includes('.')) return false;
  
  const parts = token.split('.');
  if (parts.length !== 2) return false;
  
  const [payloadB64, signatureB64] = parts;

  try {
    const enc = new TextEncoder();
    const key = await crypto.subtle.importKey(
      'raw',
      enc.encode(AUTH_SECRET),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    );

    const sigBytes = base64urlToBytes(signatureB64);
    const dataBytes = enc.encode(payloadB64);

    const isValid = await crypto.subtle.verify(
      'HMAC',
      key,
      sigBytes,
      dataBytes
    );

    if (!isValid) return false;

    // Verify expiration payload
    let b64 = payloadB64.replace(/-/g, '+').replace(/_/g, '/');
    while (b64.length % 4) b64 += '=';
    const payload = JSON.parse(atob(b64));

    if (!payload.authenticated || typeof payload.exp !== 'number') return false;
    if (Date.now() > payload.exp) return false;

    return true;
  } catch (e) {
    return false;
  }
}

export default async function middleware(request) {
  const url = new URL(request.url);
  const pathname = url.pathname;

  // 1. Whitelist public assets & authentication endpoints
  if (
    pathname === '/login' ||
    pathname === '/login.html' ||
    pathname === '/api/auth' ||
    pathname === '/api/logout' ||
    pathname.startsWith('/_next') ||
    pathname.endsWith('.ico') ||
    pathname.endsWith('.png') ||
    pathname.endsWith('.jpg') ||
    pathname.endsWith('.svg')
  ) {
    return;
  }

  // 2. Extract session cookie
  const cookieHeader = request.headers.get('cookie') || '';
  const match = cookieHeader.match(/octane_session=([^;]+)/);
  const token = match ? match[1] : null;

  const isAuthenticated = await verifySessionToken(token);

  if (isAuthenticated) {
    return; // Pass through to dashboard assets and APIs
  }

  // 3. Unauthenticated access handling
  if (pathname.startsWith('/api/')) {
    return new Response(JSON.stringify({ error: 'Unauthorized: Session required' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // Redirect all page & JS requests to /login
  const loginUrl = new URL('/login', request.url);
  return Response.redirect(loginUrl, 302);
}

export const config = {
  matcher: [
    '/',
    '/dashboard_enterprise.html',
    '/dashboard_enterprise.js',
    '/api/:path*'
  ]
};
