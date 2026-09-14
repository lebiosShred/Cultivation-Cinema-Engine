const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

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

function classifyChannel(lead) {
  const src = (lead.source || '').toLowerCase();
  const evt = (lead.conversionEvent || lead.event || '').toLowerCase();
  const raw = (lead.rawEventName || '').toLowerCase();
  const url = (lead.landingUrl || '').toLowerCase();

  // 1. HubSpot Calendar demo bookings
  if (url.includes('meetings.hubspot.com') || evt.includes('calendar booking') || evt.includes('tm1 demo calendar')) {
    return { channelId: 'meeting', channelLabel: 'Calendar Booking', channelIcon: '📅' };
  }

  // 2. Email outreach and Chrome extension sync
  if (evt.includes('extension') || raw.includes('extension') || src.includes('extension') || evt.includes('email')) {
    return { channelId: 'email', channelLabel: 'Email Outreach', channelIcon: '📧' };
  }

  // 3. Google Organic Search
  if (src.includes('google') || src.includes('search')) {
    return { channelId: 'search', channelLabel: 'Google Search', channelIcon: '🔍' };
  }

  // 4. Website forms, downloads, and event RSVPs
  if (
    url.includes('octanesolutions.com.au') ||
    url.startsWith('/') ||
    evt.includes('form') ||
    evt.includes('trial') ||
    evt.includes('rsvp') ||
    evt.includes('download') ||
    evt.includes('webinar')
  ) {
    if (!url.includes('hubspot portal') && !url.includes('direct crm')) {
      return { channelId: 'website', channelLabel: 'Website Form', channelIcon: '🌐' };
    }
  }

  // 5. Direct CRM contacts
  return { channelId: 'direct', channelLabel: 'Direct CRM', channelIcon: '👤' };
}

let cachedLeads = null;
function loadLeads() {
  if (cachedLeads) return cachedLeads;
  try {
    const filePath = path.join(__dirname, '..', 'data', 'leads_store.json');
    if (fs.existsSync(filePath)) {
      cachedLeads = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } else {
      cachedLeads = { '24h': [], '7d': [], '30d': [], '90d': [] };
    }
  } catch (err) {
    cachedLeads = { '24h': [], '7d': [], '30d': [], '90d': [] };
  }
  return cachedLeads;
}

module.exports = async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  // Check auth session cookie
  const cookies = parseCookies(req.headers.cookie);
  const sessionToken = cookies['octane_session'];

  if (!verifySessionToken(sessionToken)) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Active Octane authentication session required to inspect CRM customer leads.'
    });
  }

  const allLeads = loadLeads();
  const tf = req.query.timeframe || '90d';
  let rawList = allLeads[tf] || allLeads['90d'] || [];

  // Classify each lead
  let leads = rawList.map(l => {
    const ch = classifyChannel(l);
    return {
      ...l,
      ...ch
    };
  });

  // Calculate channel summary stats before filters
  const channelCounts = {
    all: leads.length,
    marketing: leads.filter(l => l.channelId !== 'direct').length,
    website: leads.filter(l => l.channelId === 'website').length,
    email: leads.filter(l => l.channelId === 'email').length,
    meeting: leads.filter(l => l.channelId === 'meeting').length,
    search: leads.filter(l => l.channelId === 'search').length,
    direct: leads.filter(l => l.channelId === 'direct').length
  };

  // Optional channel filter
  const channel = req.query.channel;
  if (channel && channel !== 'all') {
    if (channel === 'marketing') {
      leads = leads.filter(l => l.channelId !== 'direct');
    } else {
      leads = leads.filter(l => l.channelId === channel);
    }
  }

  // Optional category filter
  const category = req.query.category;
  if (category && category !== 'all') {
    leads = leads.filter(l => l.category === category);
  }

  // Optional search query
  const q = req.query.q;
  if (q && typeof q === 'string') {
    const qLower = q.toLowerCase();
    leads = leads.filter(l => 
      (l.name && l.name.toLowerCase().includes(qLower)) ||
      (l.company && l.company.toLowerCase().includes(qLower)) ||
      (l.email && l.email.toLowerCase().includes(qLower)) ||
      (l.jobTitle && l.jobTitle.toLowerCase().includes(qLower)) ||
      (l.channelLabel && l.channelLabel.toLowerCase().includes(qLower)) ||
      (l.landingUrl && l.landingUrl.toLowerCase().includes(qLower))
    );
  }

  return res.status(200).json({
    success: true,
    timeframe: tf,
    total: leads.length,
    channelCounts,
    leads
  });
};
