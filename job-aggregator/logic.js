// Shared job-aggregator rules. Injected into n8n Code nodes by build_workflow.py.
// Keep this file free of n8n helpers, require(), and module.exports.

const VARIANT_NAMES = [
  'AI/ML Engineer',
  'Computer Vision Engineer',
  'Full-Stack Software Engineer',
  'Generative AI Engineer',
];

const SHEET_COLUMNS = [
  'Title',
  'Company',
  'Location',
  'Match Score',
  'Best Variant',
  'Resume Link',
  'Job Link',
  'Application Method',
  'Email Status',
  'DM Message',
  'Status',
];

function asText(value) {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return value.map(asText).filter(Boolean).join(', ');
  if (typeof value === 'object') {
    return asText(value.name || value.label || value.linkedinText || value.text || value.city || value.address || '');
  }
  return String(value);
}

function normalizeText(text) {
  return asText(text)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function padWords(text) {
  return ` ${normalizeText(text).replace(/[^a-z]+/g, ' ').trim()} `;
}

function stripHtml(raw) {
  return asText(raw)
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&#64;|&#x40;/gi, '@')
    .replace(/&quot;/gi, '"')
    .replace(/\s+/g, ' ')
    .trim();
}

function deobfuscateEmails(text) {
  return asText(text)
    .replace(/\s*[\[{(]\s*at\s*[\]})]\s*/gi, '@')
    .replace(/\s*[\[{(]\s*dot\s*[\]})]\s*/gi, '.');
}

function isPlausibleEmail(email) {
  const value = asText(email).trim().toLowerCase();
  if (value.length < 6 || value.length > 80) return false;
  if (!/^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i.test(value)) return false;
  if (/\.(png|jpe?g|gif|webp|svg)$/i.test(value)) return false;
  if (/(example\.com|domain\.com|email\.com|sentry\.io|wixpress\.com|schema\.org|cloudflare\.com)$/i.test(value)) return false;
  if (/^(noreply|no-reply|donotreply)@/i.test(value)) return false;
  return true;
}

function extractEmails(text) {
  const found = deobfuscateEmails(stripHtml(text)).match(/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/gi) || [];
  const out = [];
  const seen = new Set();
  for (const candidate of found) {
    const email = candidate.toLowerCase().replace(/\.+$/, '');
    if (seen.has(email) || !isPlausibleEmail(email)) continue;
    seen.add(email);
    out.push(email);
  }
  return out;
}

function asEmailList(value) {
  if (Array.isArray(value)) {
    return [...new Set(value.map((item) => asText(item).trim().toLowerCase()).filter(isPlausibleEmail))];
  }
  if (typeof value === 'string') return extractEmails(value);
  return [];
}

function smartExcerpt(text, limit, emails) {
  const clean = asText(text).replace(/\s+/g, ' ').trim();
  const uniqueEmails = asEmailList(emails);
  const extra = uniqueEmails.length ? ` Contact emails: ${uniqueEmails.join(', ')}.` : '';
  const max = Math.max(80, Number(limit) || 900);
  const budget = Math.max(40, max - extra.length);
  let body = clean;
  if (body.length > budget) {
    const tailLen = Math.max(20, Math.floor(budget * 0.32));
    const headLen = Math.max(20, budget - tailLen - 5);
    const head = clean.slice(0, headLen).trim();
    const tail = clean.slice(-tailLen).trim();
    body = `${head} ... ${tail}`;
  }
  const combined = `${body}${extra}`.trim();
  return combined.length <= max ? combined : combined.slice(0, max);
}

function prepareText(raw, limit) {
  const text = deobfuscateEmails(stripHtml(raw));
  const emails = extractEmails(text).slice(0, 5);
  return {
    description: smartExcerpt(text, limit, emails),
    emails_found: emails,
  };
}

function absoluteUrl(link, origin) {
  const value = asText(link).trim();
  if (!value) return '';
  if (/^https?:\/\//i.test(value)) return value;
  if (value.startsWith('//')) return `https:${value}`;
  if (value.startsWith('/')) return `${origin}${value}`;
  return `${origin}/${value}`;
}

function isErrorPayload(row) {
  if (!row || typeof row !== 'object' || Array.isArray(row)) return true;
  if (row._empty || row.legal) return true;
  const hasTitle = asText(row.title || row.position || row.positionName).trim();
  if (row.error && !hasTitle) return true;
  return false;
}

function unwrapRows(rows) {
  const list = Array.isArray(rows) ? rows.filter((row) => row != null) : [];
  if (list.length === 1 && Array.isArray(list[0])) return list[0];
  if (list.length === 1 && list[0] && Array.isArray(list[0].data) && !list[0].title) return list[0].data;
  if (list.length === 1 && list[0] && Array.isArray(list[0].jobs) && !list[0].title && !list[0].positionName) return list[0].jobs;
  if (list.length === 1 && list[0] && Array.isArray(list[0].raw_jobs)) return list[0].raw_jobs;
  return list;
}

function baseJob({ title, company, location, link, description, source, regionHint, excerptChars }) {
  const cleanTitle = asText(title).replace(/\s+/g, ' ').trim();
  if (!cleanTitle) return null;
  const prepared = prepareText(description, excerptChars || 900);
  return {
    title: cleanTitle,
    company: asText(company).replace(/\s+/g, ' ').trim() || 'Unknown',
    location: asText(location).replace(/\s+/g, ' ').trim(),
    link: asText(link).trim(),
    description: prepared.description,
    emails_found: prepared.emails_found,
    source: source || '',
    region_hint: regionHint || '',
  };
}

function normalizeRemoteOk(row, excerptChars) {
  if (isErrorPayload(row)) return null;
  const id = asText(row.id || row.slug);
  const link = asText(row.apply_url || row.url || (id ? `https://remoteok.com/remote-jobs/${id}` : ''));
  return baseJob({
    title: row.position || row.title,
    company: row.company,
    location: row.location || 'Remote',
    link,
    description: row.description,
    source: 'RemoteOK',
    regionHint: 'remote',
    excerptChars,
  });
}

function normalizeJooble(row, excerptChars, regionHint) {
  if (isErrorPayload(row)) return null;
  return baseJob({
    title: row.title,
    company: row.company,
    location: row.location,
    link: row.link || row.url,
    description: row.snippet || row.description,
    source: 'Jooble',
    regionHint,
    excerptChars,
  });
}

function normalizeLinkedIn(row, excerptChars) {
  if (isErrorPayload(row)) return null;
  const locationText = asText(row.location || row.place);
  const remote = /remote|work from home/i.test(`${locationText} ${asText(row.title)}`);
  return baseJob({
    title: row.title,
    company: row.companyName || row.company || (row.companyDetails && row.companyDetails.name),
    location: locationText,
    link: row.link || row.url || row.jobUrl || row.applyUrl,
    description: row.descriptionText || row.description || row.text,
    source: 'LinkedIn',
    regionHint: remote ? 'remote' : '',
    excerptChars,
  });
}

function normalizeIndeed(row, excerptChars, regionHint) {
  if (isErrorPayload(row)) return null;
  const locationText = asText(row.location);
  let hint = regionHint || '';
  if (!hint && /karachi/i.test(locationText)) hint = 'karachi';
  if (!hint && /remote/i.test(locationText)) hint = 'remote';
  return baseJob({
    title: row.positionName || row.title || row.position,
    company: row.company || row.companyName,
    location: locationText,
    link: row.url || row.externalApplyLink || row.link,
    description: row.description || row.summary || row.snippet,
    source: 'Indeed',
    regionHint: hint,
    excerptChars,
  });
}

function normalizeRozee(row, excerptChars) {
  if (isErrorPayload(row)) return null;
  const companyFull = asText(row.company);
  let company = companyFull;
  let location = asText(row.location);
  if (!location && companyFull.includes(',')) {
    const parts = companyFull.split(',');
    company = parts.shift().trim();
    location = parts.join(',').trim();
  }
  return baseJob({
    title: row.title,
    company,
    location: location || 'Karachi',
    link: absoluteUrl(row.link || row.url, 'https://www.rozee.pk'),
    description: row.description,
    source: 'Rozee',
    regionHint: 'karachi',
    excerptChars,
  });
}

function mentionsOtherCountry(location) {
  const padded = padWords(location);
  const raw = normalizeText(location);
  const phrases = ['united states', 'united kingdom', 'new york', 'san francisco', 'los angeles'];
  if (phrases.some((phrase) => raw.includes(phrase))) return true;
  const tokens = [
    'usa', 'uk', 'canada', 'australia', 'germany', 'india', 'uae', 'dubai', 'singapore',
    'nigeria', 'poland', 'spain', 'france', 'texas', 'california', 'london', 'toronto',
    'berlin', 'seoul', 'philippines', 'europe', 'netherlands', 'sweden', 'ireland',
    'brazil', 'mexico', 'japan', 'china',
  ];
  return tokens.some((token) => padded.includes(` ${token} `));
}

function isOtherPakistanCity(location) {
  const padded = padWords(location);
  if (padded.includes(' karachi ')) return false;
  const cities = ['lahore', 'islamabad', 'rawalpindi', 'faisalabad', 'peshawar', 'quetta', 'multan', 'hyderabad'];
  return cities.some((city) => padded.includes(` ${city} `));
}

function isRemoteJob(job) {
  const padded = `${padWords(job.location)} ${padWords(job.title)}`;
  if (padded.includes(' remote ') || padded.includes(' work from home ') || padded.includes(' wfh ')) return true;
  if (job.region_hint === 'remote') return true;
  if (normalizeText(job.source) === 'remoteok') return true;
  return false;
}

function roleRelevant(job) {
  const text = `${asText(job.title)} ${asText(job.description)}`;
  return /\b(ai|a\.i\.|ml|machine learning|deep learning|data|python|software|developer|engineer|intern|internship|full[\s-]?stack|computer vision|llm|nlp|backend|frontend|generative|pytorch|tensorflow|scientist)\b/i.test(text);
}

function keepJob(job) {
  if (!job || !asText(job.title).trim()) return false;
  const location = job.location || '';
  if (padWords(location).includes(' karachi ')) return true;
  if (isRemoteJob(job) && !mentionsOtherCountry(location)) return true;
  if (job.region_hint === 'karachi' && !mentionsOtherCountry(location) && !isOtherPakistanCity(location)) return true;
  return false;
}

function dedupKey(job) {
  const link = asText(job.link).trim().toLowerCase();
  if (link) return `link:${link}`;
  return `${normalizeText(job.title)}|${normalizeText(job.company)}`;
}

function dedupJobs(jobs) {
  const seen = new Set();
  const unique = [];
  for (const job of jobs) {
    if (!job || !asText(job.title).trim() || job._empty || job._noJobs) continue;
    const key = dedupKey(job);
    if (seen.has(key)) continue;
    seen.add(key);
    unique.push(job);
  }
  return unique;
}

function capBySource(jobs, maxJobs) {
  const max = Math.max(1, Number(maxJobs) || 12);
  const buckets = new Map();
  for (const job of jobs) {
    const key = job.source || 'other';
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(job);
  }
  const out = [];
  let added = true;
  while (out.length < max && added) {
    added = false;
    for (const list of buckets.values()) {
      if (list.length && out.length < max) {
        out.push(list.shift());
        added = true;
      }
    }
  }
  return out;
}

function selectJobs(jobs, maxJobs) {
  const real = dedupJobs(jobs);
  const located = real.filter(keepJob);
  const filtered = located.filter(roleRelevant);
  const capped = capBySource(filtered, maxJobs);
  let reason = '';
  if (!real.length) {
    reason = 'No jobs were returned. Check the Apify and Jooble keys in Config, then run again.';
  } else if (!located.length) {
    reason = `${real.length} roles were found, but none were Karachi-based or remote.`;
  } else if (!filtered.length) {
    reason = `${located.length} Karachi or remote roles were found, but none matched AI, ML, data, or software titles.`;
  }
  return {
    jobs: capped,
    considered: real.length,
    matchedLocation: located.length,
    reason,
  };
}

function parseModelJson(content) {
  if (content && typeof content === 'object' && !Array.isArray(content)) return content;
  let text = asText(content).trim();
  if (!text) throw new Error('empty model response');
  const fence = text.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) text = fence[1].trim();
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start === -1 || end <= start) throw new Error('no json object');
  return JSON.parse(text.slice(start, end + 1));
}

function groqText(payload) {
  if (!payload || typeof payload !== 'object') return '';
  const body = payload.groq_response && typeof payload.groq_response === 'object' ? payload.groq_response : payload;
  const choice = body.choices && body.choices[0];
  if (!choice) return '';
  const message = choice.message || {};
  const content = message.content != null ? message.content : choice.text;
  if (Array.isArray(content)) return content.map((part) => asText(part.text || part.content)).join('\n');
  return asText(content);
}

function coerceScore(value) {
  const match = asText(value).match(/\d+/);
  if (!match) return 0;
  const score = parseInt(match[0], 10);
  if (Number.isNaN(score)) return 0;
  return Math.max(0, Math.min(100, score));
}

function coerceVariant(name) {
  const raw = asText(name).trim().toLowerCase();
  return VARIANT_NAMES.find((variant) => variant.toLowerCase() === raw) || 'AI/ML Engineer';
}

function blankish(value) {
  const text = asText(value).trim().toLowerCase();
  return !text || text === 'empty' || text === 'n/a' || text === 'none' || text === '-';
}

function fallbackEmail(job) {
  const variant = job.best_variant || 'AI/ML Engineer';
  const link = job.resume_link || '';
  const subject = `Application for ${job.title} - Madiha Shahid`;
  const lines = [
    'Dear Hiring Team,',
    '',
    `I am writing to apply for the ${job.title} role at ${job.company}. I am a final-year Computer Science student specializing in AI/ML, with project work in Python, PyTorch, and applied machine learning.`,
    '',
    link
      ? `My ${variant} resume is here: ${link}`
      : `I am applying with my ${variant} resume and would be glad to share it.`,
    '',
    'Thank you for your time. I would welcome the chance to discuss how I can contribute.',
    '',
    'Best regards,',
    'Madiha Shahid',
  ];
  return { subject, body: lines.join('\n') };
}

function decideApplication(job, parsed) {
  const emails = asEmailList(job.emails_found);
  const model = parsed && typeof parsed === 'object' ? parsed : {};
  const allowed = {
    email: 'email',
    external_link: 'job link',
    link: 'job link',
    dm: 'direct message',
    phone: 'phone',
    form: 'form',
    other: 'other',
    none: 'not listed',
  };
  let method = allowed[asText(model.method).trim().toLowerCase()] || 'not listed';
  const modelEmail = asText(model.email_address).trim().toLowerCase();
  const verified = emails.find(isPlausibleEmail) || '';
  let email = '';
  let send = false;

  if (verified) {
    method = 'email';
    email = emails.includes(modelEmail) ? modelEmail : verified;
    send = true;
  } else if (method === 'email') {
    method = job.link ? 'job link' : 'not listed';
  }

  const fallback = fallbackEmail(job);
  let subject = blankish(model.email_subject) ? fallback.subject : asText(model.email_subject).trim();
  let body = blankish(model.email_body) ? fallback.body : asText(model.email_body).trim();
  if (send && job.resume_link && !body.includes(job.resume_link)) {
    body = body.replace(/\battached\b/gi, 'linked below');
    body += `\n\nResume (${job.best_variant || 'selected variant'}): ${job.resume_link}`;
  }
  if (!send) {
    subject = '';
    body = '';
  }

  const dm = method === 'direct message' ? asText(model.dm_message).trim() : '';
  const notes = asText(model.other_notes).trim();
  let status = 'Review the job link';
  if (method === 'email' && send) status = 'Email queued';
  else if (method === 'job link') status = 'Apply via link';
  else if (method === 'direct message') status = 'DM drafted';
  else if (method === 'phone') status = 'Call or contact';
  else if (method === 'form') status = 'Apply via form';
  else if (method === 'other') status = 'See notes';
  else if (method === 'not listed') status = job.link ? 'Review the job link' : 'No application method found';

  return {
    ...job,
    emails_found: emails,
    application_method: method,
    email_address: email,
    email_subject: subject,
    email_body: body,
    dm_message: dm || notes,
    send_email: send,
    status,
  };
}

function emptySheetRow(reason) {
  return {
    Title: '(no matching jobs this run)',
    Company: '',
    Location: '',
    'Match Score': '',
    'Best Variant': '',
    'Resume Link': '',
    'Job Link': '',
    'Application Method': '',
    'Email Status': 'Not sent',
    'DM Message': '',
    Status: asText(reason) || 'No matching jobs this run.',
    email_address: '',
    email_subject: '',
    email_body: '',
    send_email: false,
  };
}

function toTransport(job) {
  const send = !!(job && job.send_email && isPlausibleEmail(job.email_address));
  return {
    Title: asText(job.title).trim(),
    Company: asText(job.company).trim(),
    Location: asText(job.location).trim(),
    'Match Score': job.match_score == null || job.match_score === '' ? '' : String(job.match_score),
    'Best Variant': asText(job.best_variant).trim(),
    'Resume Link': asText(job.resume_link).trim(),
    'Job Link': asText(job.link).trim(),
    'Application Method': asText(job.application_method).trim(),
    'Email Status': send ? 'Queued' : 'Not sent',
    'DM Message': asText(job.dm_message).trim(),
    Status: asText(job.status).trim(),
    email_address: send ? asText(job.email_address).trim().toLowerCase() : '',
    email_subject: send ? asText(job.email_subject).trim() : '',
    email_body: send ? asText(job.email_body).trim() : '',
    send_email: send,
  };
}

function applyEmailCap(rows, maxEmails) {
  const max = Math.max(0, Number(maxEmails) || 0);
  let queued = 0;
  return rows.map((row) => {
    const next = { ...row };
    if (!next.send_email) return next;
    if (queued < max) {
      queued += 1;
      return next;
    }
    next.send_email = false;
    next.email_address = '';
    next.email_subject = '';
    next.email_body = '';
    next['Email Status'] = 'Not sent - daily cap';
    next.Status = `A real application email was found, but this run already queued ${max} emails. Raise maxEmailsPerRun in Config to send more.`;
    return next;
  });
}

function filterByScore(jobs, minScore) {
  const minimum = Number(minScore);
  const floor = Number.isNaN(minimum) ? 50 : minimum;
  const rows = (jobs || []).filter((job) => job && asText(job.title).trim() && !job._empty && !job._noJobs);
  const kept = rows.filter((job) => Number(job.match_score) >= floor);
  let reason = '';
  if (!kept.length) {
    if (!rows.length) reason = 'No scored jobs were returned.';
    else if (rows.every((job) => !Number(job.match_score))) {
      reason = 'Jobs were found, but scoring did not return a score. Check the Groq API key in Config.';
    } else {
      reason = `No role scored at or above ${floor}. Lower minMatchScore in Config if you want more results.`;
    }
  }
  return { jobs: kept, reason };
}
