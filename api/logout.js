module.exports = async function handler(req, res) {
  const cookieHeader = 'octane_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0';
  res.setHeader('Set-Cookie', cookieHeader);

  // If requested via browser GET navigation, redirect directly to login
  if (req.method === 'GET') {
    res.writeHead(302, { Location: '/login' });
    return res.end();
  }

  return res.status(200).json({ success: true, redirect: '/login' });
};
