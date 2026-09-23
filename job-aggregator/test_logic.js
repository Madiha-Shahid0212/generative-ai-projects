const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(path.join(__dirname, 'logic.js'), 'utf8');
const context = { console };
vm.createContext(context);
vm.runInContext(`${source}\n;this.api = { VARIANT_NAMES, SHEET_COLUMNS, extractEmails, prepareText, smartExcerpt, normalizeRemoteOk, normalizeJooble, normalizeLinkedIn, normalizeIndeed, normalizeRozee, selectJobs, parseModelJson, groqText, decideApplication, toTransport, applyEmailCap, filterByScore, emptySheetRow, keepJob, capBySource };`, context);
const api = context.api;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const longTail = `${'We build models. '.repeat(400)}How to apply: email careers [at] acme [dot] com today.`;
const prepared = api.prepareText(longTail, 900);
assert(prepared.description.length <= 900, 'excerpt stays within the Groq-safe limit');
assert(prepared.emails_found.includes('careers@acme.com'), 'email is taken from the full description, not the truncated head');
assert(prepared.description.includes('How to apply'), 'the apply instructions at the end are kept');
assert(prepared.description.includes('careers@acme.com'), 'the excerpt still shows the extracted email');
assert(!longTail.slice(0, 250).includes('careers@acme.com'), 'the old 250-character cut would have dropped this email');

const htmlJob = '<p>Apply to <b>jobs@brightlabs.io</b></p><img src="pic@2x.png">';
assert(api.extractEmails(htmlJob).join() === 'jobs@brightlabs.io', 'html is ignored and image names are not emails');
assert(!api.extractEmails('Write to name@example.com or noreply@acme.com').length, 'placeholders and noreply addresses are ignored');

const remote = api.normalizeRemoteOk({
  legal: 'Remote OK legal notice',
}, 900);
assert(remote === null, 'RemoteOK legal header is skipped');

const remoteJob = api.normalizeRemoteOk({
  id: '99',
  position: 'ML Engineer',
  company: 'Northstar',
  location: '',
  description: '<p>Remote pytorch role. Apply jobs@northstar.dev</p>',
  apply_url: 'https://northstar.dev/jobs/99',
}, 900);
assert(remoteJob.company === 'Northstar', 'RemoteOK company is read from company');
assert(remoteJob.link === 'https://northstar.dev/jobs/99', 'RemoteOK uses the apply link');
assert(remoteJob.region_hint === 'remote', 'RemoteOK jobs are marked remote');
assert(remoteJob.emails_found.includes('jobs@northstar.dev'), 'RemoteOK description emails are kept');

const linkedin = api.normalizeLinkedIn({
  title: 'AI Engineer',
  companyName: 'PakAI',
  location: 'Karachi, Sindh, Pakistan',
  link: 'https://www.linkedin.com/jobs/view/1',
  descriptionText: `${'x'.repeat(2000)} Send your CV to hr@pakai.com`,
}, 900);
assert(linkedin.company === 'PakAI', 'LinkedIn companyName maps to company');
assert(linkedin.emails_found.includes('hr@pakai.com'), 'LinkedIn email beyond the old cutoff is kept');

const indeed = api.normalizeIndeed({
  positionName: 'Python Developer',
  company: 'Harbor',
  location: 'Karachi',
  url: 'https://pk.indeed.com/viewjob?jk=abc',
  description: 'Karachi python role',
}, 900, 'karachi');
assert(indeed.title === 'Python Developer' && indeed.link.includes('indeed.com'), 'Indeed fields are normalized');

const rozee = api.normalizeRozee({
  title: 'AI Engineer',
  link: '//www.rozee.pk/job/ai-engineer',
  company: 'DataHouse, Karachi',
  description: 'Build models',
}, 900);
assert(rozee.link === 'https://www.rozee.pk/job/ai-engineer', 'protocol-relative Rozee links become https');
assert(rozee.company === 'DataHouse', 'Rozee company is split from the location');

const selected = api.selectJobs([
  remoteJob,
  linkedin,
  indeed,
  { ...indeed, link: 'https://pk.indeed.com/viewjob?jk=abc' },
  api.normalizeJooble({ title: 'Backend Engineer', company: 'London Co', location: 'London, United Kingdom', link: 'https://jooble.org/london', snippet: 'UK only' }, 900, 'remote'),
  api.normalizeJooble({ title: 'Onsite Dev', company: 'Lhr', location: 'Lahore, Pakistan', link: 'https://jooble.org/lhr', snippet: 'office role' }, 900, ''),
  api.normalizeJooble({ title: 'Karachi Intern', company: 'Studio', location: 'Gulshan, Karachi', link: 'https://jooble.org/khi', snippet: 'internship' }, 900, 'karachi'),
  { _empty: true },
], 10);
const titles = selected.jobs.map((job) => job.title);
assert(titles.includes('ML Engineer'), 'remote jobs are kept');
assert(titles.includes('AI Engineer'), 'Karachi LinkedIn jobs are kept');
assert(titles.includes('Karachi Intern'), 'Karachi Jooble jobs are kept');
assert(!titles.includes('Backend Engineer'), 'remote roles locked to another country are dropped');
assert(!titles.includes('Onsite Dev'), 'onsite roles outside Karachi are dropped');
assert(selected.jobs.filter((job) => job.link.includes('jk=abc')).length === 1, 'duplicate links collapse to one job');

const sales = api.normalizeRemoteOk({
  id: 'sales',
  position: 'Sales Manager',
  company: 'Quota',
  location: 'Remote',
  description: 'Own the pipeline and close enterprise deals.',
}, 900);
const withoutSales = api.selectJobs([sales, remoteJob], 10);
assert(withoutSales.jobs.map((job) => job.title).join() === 'ML Engineer', 'unrelated remote roles do not use a scoring slot');

const fair = api.capBySource([
  { title: 'a1', company: 'A', source: 'A', link: '1' },
  { title: 'a2', company: 'A', source: 'A', link: '2' },
  { title: 'a3', company: 'A', source: 'A', link: '3' },
  { title: 'b1', company: 'B', source: 'B', link: '4' },
  { title: 'b2', company: 'B', source: 'B', link: '5' },
], 4);
assert(fair.map((job) => job.source).join() === 'A,B,A,B', 'the scoring cap rotates across sources');

const fenced = 'Sure\n```json\n{"match_score":"82%","summary":"Python and PyTorch overlap"}\n```';
const parsed = api.parseModelJson(fenced);
assert(parsed.match_score === '82%', 'json is parsed from a fenced model reply');
const groqPayload = { groq_response: { choices: [{ message: { content: [{ text: '{"best_variant":"Computer Vision Engineer"}' }] } }] } };
assert(api.parseModelJson(api.groqText(groqPayload)).best_variant === 'Computer Vision Engineer', 'Groq content arrays are read');

const decided = api.decideApplication({
  ...linkedin,
  match_score: 80,
  best_variant: 'AI/ML Engineer',
  resume_link: 'https://drive.google.com/resume',
}, {
  method: 'none',
  email_address: 'invented@not-real.test',
  email_body: 'I am attaching my resume.',
});
assert(decided.send_email === true, 'a real address in the full description still sends');
assert(decided.email_address === 'hr@pakai.com', 'an invented address is not used');
assert(decided.email_body.includes('https://drive.google.com/resume'), 'the email contains the resume link');
assert(!/\battached\b/i.test(decided.email_body), 'the email does not claim a file is attached');

const inventedOnly = api.decideApplication({
  title: 'AI Engineer',
  company: 'NoMail',
  location: 'Karachi',
  link: 'https://jobs.example/1',
  emails_found: [],
  resume_link: 'https://drive.google.com/resume',
}, {
  method: 'email',
  email_address: 'hallucinated@company.com',
  email_subject: 'Hello',
  email_body: 'Hire me',
});
assert(inventedOnly.send_email === false, 'emails that are not in the description are not sent');
assert(inventedOnly.application_method === 'job link', 'unverified email methods fall back to the job link');

const transport = api.toTransport(decided);
for (const column of api.SHEET_COLUMNS) {
  assert(Object.prototype.hasOwnProperty.call(transport, column), `sheet row includes ${column}`);
}
assert(transport['Email Status'] === 'Queued', 'verified emails are queued for Gmail');

const capped = api.applyEmailCap([
  transport,
  api.toTransport({ ...decided, email_address: 'second@pakai.com', emails_found: ['second@pakai.com'] }),
], 1);
assert(capped[0].send_email === true, 'the first verified email is kept');
assert(capped[1].send_email === false && capped[1]['Email Status'] === 'Not sent - daily cap', 'later emails stay on the sheet without being sent');

const failedScores = api.filterByScore([
  { title: 'Role', match_score: 0 },
], 50);
assert(!failedScores.jobs.length && /Groq API key/.test(failedScores.reason), 'failed scoring explains that the sheet row is a scoring failure');

const lowScores = api.filterByScore([
  { title: 'Role', match_score: 40 },
], 50);
assert(/minMatchScore/.test(lowScores.reason), 'scores under the cutoff name the threshold');

const empty = api.emptySheetRow('nothing today');
assert(empty.send_email === false && empty.Title.includes('no matching jobs'), 'an empty run still has a sheet row');

console.log('logic tests passed');
