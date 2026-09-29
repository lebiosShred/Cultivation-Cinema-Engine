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

const HUBSPOT_TOKEN = process.env.HUBSPOT_ACCESS_TOKEN || '';
let cachedLeads = null;
let lastCacheTime = 0;
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

function loadLocalStore() {
  try {
    const filePath = path.join(__dirname, '..', 'data', 'leads_store.json');
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    }
  } catch (err) {}
  return { '24h': [], '7d': [], '30d': [], '90d': [] };
}

async function fetchHubSpotContacts() {
  if (!HUBSPOT_TOKEN) return null;
  try {
    const https = require('https');
    const payload = JSON.stringify({
      sorts: [{ propertyName: 'createdate', direction: 'DESCENDING' }],
      properties: [
        'firstname', 'lastname', 'email', 'company', 'jobtitle',
        'createdate', 'lifecyclestage', 'hs_lead_status',
        'hs_analytics_source', 'hs_analytics_source_data_1', 'hs_analytics_source_data_2',
        'hs_analytics_first_url', 'hs_analytics_last_url',
        'city', 'state', 'country'
      ],
      limit: 100
    });

    const options = {
      hostname: 'api.hubapi.com',
      port: 443,
      path: '/crm/v3/objects/contacts/search',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${HUBSPOT_TOKEN}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      },
      timeout: 5000
    };

    const data = await new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            try { resolve(JSON.parse(body)); } catch (e) { reject(e); }
          } else {
            reject(new Error(`HubSpot API error ${res.statusCode}: ${body}`));
          }
        });
      });
      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('HubSpot timeout')); });
      req.write(payload);
      req.end();
    });

    const results = data.results || [];
    if (!results.length) return null;

    const now = Date.now();
    const formatted = [];

    for (const c of results) {
      const props = c.properties || {};
      const fn = (props.firstname || '').trim();
      const ln = (props.lastname || '').trim();
      const name = `${fn} ${ln}`.trim() || props.email || 'Inbound Contact';
      const createdStr = props.createdate;
      if (!createdStr) continue;

      const dt = new Date(createdStr);
      const ts = dt.getTime();
      const diffMs = now - ts;
      const diffDays = Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));

      let recency = `${diffDays} days ago`;
      if (diffDays === 0) recency = 'Today';
      else if (diffDays === 1) recency = 'Yesterday';

      const aestDt = new Date(ts + 10 * 3600 * 1000);
      const whenStr = aestDt.toISOString().replace('T', ' ').substring(0, 16) + ' AEST';

      const url = props.hs_analytics_first_url || props.hs_analytics_last_url || '';
      let landingUrl = url || 'https://www.octanesolutions.com.au/';
      let eventName = 'Website Form Submission';

      if (!url && (props.hs_analytics_source === 'OFFLINE' || !props.hs_analytics_source)) {
        landingUrl = 'Direct CRM Contact (HubSpot Portal)';
        eventName = 'Direct Sales CRM Contact (HubSpot Portal UI)';
      } else if (url.toLowerCase().includes('webinar')) {
        landingUrl = url;
        eventName = 'Webinar Registration: IBM Planning Analytics AI Agent';
      }

      const stageRaw = props.lifecyclestage || 'lead';
      const stageMap = {
        'marketingqualifiedlead': 'Marketing Qualified Lead (MQL)',
        'salesqualifiedlead': 'Sales Qualified Lead (SQL)',
        'opportunity': 'Sales Opportunity',
        'customer': 'Customer / Closed Won',
        'lead': 'Marketing Lead',
        'subscriber': 'Blog Subscriber'
      };

      const locParts = [props.city, props.state, props.country || 'Australia'].filter(Boolean);

      let companyName = (props.company || '').trim();
      if (!companyName && props.email && props.email.includes('@')) {
        const domain = props.email.split('@')[1].toLowerCase();
        if (!['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com'].includes(domain)) {
          const main = domain.split('.')[0];
          const known = {
            tractorsupply: 'Tractor Supply Company',
            veracitiz: 'Veracitiz Solutions',
            steric: 'Steric Trading',
            macquarie: 'Macquarie Group',
            unsw: 'UNSW Sydney',
            pirtek: 'Pirtek',
            resmed: 'ResMed',
            qbe: 'QBE Insurance',
            worley: 'Worley',
            tpgtelecom: 'TPG Telecom',
            standards: 'Standards Australia',
            reckitt: 'Reckitt',
            nestle: 'Nestle',
            nbnco: 'NBN Co',
            perfection: 'Perfection Fresh',
            whitehavencoal: 'Whitehaven Coal',
            storageking: 'Storage King',
            tuttbryant: 'Tutt Bryant',
            stockland: 'Stockland',
            redcape: 'Redcape Hotel Group',
            uts: 'UTS',
            westpac: 'Westpac',
            sanofi: 'Sanofi',
            woolworths: 'Woolworths'
          };
          companyName = known[main] || (main.charAt(0).toUpperCase() + main.slice(1));
        }
      }
      if (!companyName) companyName = 'Enterprise Client';

      formatted.push({
        id: `HS-${c.id}`,
        name,
        email: props.email || '',
        jobTitle: props.jobtitle || 'Executive',
        company: companyName,
        location: locParts.join(', ') || 'Australia',
        when: whenStr,
        timestamp: ts,
        diffDays,
        recency,
        conversionEvent: eventName,
        landingUrl,
        source: props.hs_analytics_source || 'HubSpot CRM',
        lifecycleStage: stageMap[stageRaw.toLowerCase()] || stageRaw,
        status: props.hs_lead_status || 'IN_PROGRESS',
        category: 'planning',
        categoryLabel: 'Planning Analytics',
        badgeClass: 'badge-plan',
        isInternal: false,
        rawEventName: eventName
      });
    }

    // Merge with local store to preserve full 90-day history while having fresh top records
    const local = loadLocalStore();
    const local90 = local['90d'] || [];
    const idMap = new Map();
    formatted.forEach(l => idMap.set(l.id, l));
    local90.forEach(l => { if (!idMap.has(l.id)) idMap.set(l.id, l); });

    const allCombined = Array.from(idMap.values());
    allCombined.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));

    return {
      '24h': allCombined.filter(l => l.diffDays <= 1),
      '7d': allCombined.filter(l => l.diffDays <= 7),
      '30d': allCombined.filter(l => l.diffDays <= 30),
      '90d': allCombined.filter(l => l.diffDays <= 90)
    };
  } catch (e) {
    return null;
  }
}

async function loadLeads() {
  const now = Date.now();
  if (cachedLeads && (now - lastCacheTime < CACHE_TTL_MS)) {
    return cachedLeads;
  }

  // Try live fetch from HubSpot
  const live = await fetchHubSpotContacts();
  if (live && live['7d'] && live['7d'].length > 0) {
    cachedLeads = live;
    lastCacheTime = now;
    return cachedLeads;
  }

  // Fallback to local leads store
  cachedLeads = loadLocalStore();
  lastCacheTime = now;
  return cachedLeads;
}

module.exports = async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  // Check auth session via cookie, Bearer header, or query param
  const cookies = parseCookies(req.headers.cookie);
  let sessionToken = cookies['octane_session'];

  if (!sessionToken && req.headers.authorization) {
    const authHeader = req.headers.authorization;
    if (authHeader.toLowerCase().startsWith('bearer ')) {
      sessionToken = authHeader.slice(7).trim();
    }
  }

  if (!sessionToken && req.query && req.query.token) {
    sessionToken = req.query.token;
  }

  if (!verifySessionToken(sessionToken)) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Active Octane authentication session required to inspect CRM customer leads.'
    });
  }

  const allLeads = await loadLeads();
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
  const demosCount = leads.filter(l => 
    l.channelId === 'meeting' || 
    (l.conversionEvent || '').toLowerCase().includes('calendar') || 
    (l.conversionEvent || '').toLowerCase().includes('demo')
  ).length;

  const channelCounts = {
    all: leads.length,
    marketing: leads.filter(l => l.channelId !== 'direct').length,
    website: leads.filter(l => l.channelId === 'website').length,
    email: leads.filter(l => l.channelId === 'email').length,
    meeting: leads.filter(l => l.channelId === 'meeting').length,
    search: leads.filter(l => l.channelId === 'search').length,
    direct: leads.filter(l => l.channelId === 'direct').length,
    demos: demosCount
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
