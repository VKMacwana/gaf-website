// Shared relay for website forms that store answers in Google Forms. Each form's
// endpoint checks a Cloudflare Turnstile token, a honeypot field and the time
// taken to fill the form, then forwards the answers to Google Forms from the
// server, so the Google Form ID (held in an env var) never appears in page source.

const HONEYPOT_FIELD = 'website';
const STARTED_FIELD = 'form_started';
const MIN_FILL_MS = 5000;
const MAX_FILL_MS = 24 * 60 * 60 * 1000;
const MAX_BODY_BYTES = 20000;

function readRawBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error('too_large'));
        req.destroy();
        return;
      }
      chunks.push(c);
    });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

function checkedParams(text) {
  if (Buffer.byteLength(text, 'utf8') > MAX_BODY_BYTES) throw new Error('too_large');
  return new URLSearchParams(text);
}

async function getParams(req) {
  if (typeof req.body === 'string') return checkedParams(req.body);
  if (Buffer.isBuffer(req.body)) return checkedParams(req.body.toString('utf8'));
  if (req.body && typeof req.body === 'object') {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(req.body)) {
      for (const item of [].concat(v)) p.append(k, String(item));
    }
    return checkedParams(p.toString());
  }
  return checkedParams(await readRawBody(req));
}

function clientIp(req) {
  const fwd = req.headers['x-forwarded-for'];
  return (fwd ? String(fwd).split(',')[0] : req.socket?.remoteAddress || '').trim();
}

async function verifyTurnstile(token, ip) {
  const body = new URLSearchParams({ secret: process.env.TURNSTILE_SECRET_KEY, response: token });
  if (ip) body.append('remoteip', ip);
  const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    body,
  });
  const data = await r.json();
  return data && data.success === true;
}

// config: { formIdEnv, allowedFields, requiredFields, emailField, pagePath }
function makeFormRelay(config) {
  const allowed = new Set(config.allowedFields);

  function reply(req, res, status, payload) {
    const wantsJson = String(req.headers.accept || '').includes('application/json');
    if (wantsJson) {
      res.status(status).json(payload);
    } else {
      res.redirect(303, `${config.pagePath}?${payload.ok ? 'submitted' : 'error'}=1#apply`);
    }
  }

  return async function handler(req, res) {
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST');
      return res.status(405).json({ ok: false, error: 'method_not_allowed' });
    }
    const formId = process.env[config.formIdEnv];
    if (!formId || !process.env.TURNSTILE_SECRET_KEY) {
      return reply(req, res, 500, { ok: false, error: 'not_configured' });
    }

    let params;
    try {
      params = await getParams(req);
    } catch (e) {
      return reply(req, res, 413, { ok: false, error: 'too_large' });
    }

    // Bots that fill every field trip the honeypot; answer as if it worked so
    // they get no signal to adapt.
    if ((params.get(HONEYPOT_FIELD) || '').trim() !== '') {
      return reply(req, res, 200, { ok: true });
    }

    const started = Number(params.get(STARTED_FIELD));
    const elapsed = Date.now() - started;
    if (!Number.isFinite(started) || elapsed < MIN_FILL_MS || elapsed > MAX_FILL_MS) {
      return reply(req, res, 400, { ok: false, error: 'timing' });
    }

    const token = params.get('cf-turnstile-response');
    if (!token) return reply(req, res, 400, { ok: false, error: 'captcha' });
    try {
      if (!(await verifyTurnstile(token, clientIp(req)))) {
        return reply(req, res, 400, { ok: false, error: 'captcha' });
      }
    } catch (e) {
      return reply(req, res, 502, { ok: false, error: 'captcha_unavailable' });
    }

    for (const f of config.requiredFields) {
      if (!params.getAll(f).some((v) => v.trim() !== '')) {
        return reply(req, res, 400, { ok: false, error: 'missing_fields' });
      }
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(params.get(config.emailField).trim())) {
      return reply(req, res, 400, { ok: false, error: 'bad_email' });
    }

    const forward = new URLSearchParams();
    for (const [k, v] of params) {
      if (allowed.has(k)) forward.append(k, v.slice(0, 2000));
    }

    try {
      const g = await fetch(`https://docs.google.com/forms/d/e/${formId}/formResponse`, {
        method: 'POST',
        body: forward,
        redirect: 'manual',
      });
      if (g.status >= 400) {
        console.error('google_forms_rejected', g.status);
        return reply(req, res, 502, { ok: false, error: 'upstream' });
      }
    } catch (e) {
      console.error('google_forms_unreachable', e.message);
      return reply(req, res, 502, { ok: false, error: 'upstream' });
    }

    return reply(req, res, 200, { ok: true });
  };
}

module.exports = { makeFormRelay };
