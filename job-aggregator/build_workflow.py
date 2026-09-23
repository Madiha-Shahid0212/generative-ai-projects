#!/usr/bin/env python3
"""Build the importable n8n workflow from logic.js."""

import json
import subprocess
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOGIC = (ROOT / "logic.js").read_text()

COLUMNS = [
    "Title",
    "Company",
    "Location",
    "Match Score",
    "Best Variant",
    "Resume Link",
    "Job Link",
    "Application Method",
    "Email Status",
    "DM Message",
    "Status",
]

SPREADSHEET_ID = "13kp4sNs4XB6Q46mvdga5tSOYB-PAkZPp5xKhrfGxXBk"


def code(body: str) -> str:
    return f"{LOGIC}\n\n{body.strip()}\n"


def check_syntax(name: str, source: str) -> None:
    wrapped = "async function __check() {\n" + source + "\n}\n"
    result = subprocess.run(
        ["node", "--check", "-"],
        input=wrapped,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"Syntax error in {name}:\n{result.stderr}")


def nid() -> str:
    return str(uuid.uuid4())


def sheet_schema():
    return [
        {
            "id": column,
            "displayName": column,
            "required": False,
            "defaultMatch": False,
            "display": True,
            "type": "string",
            "canBeUsedToMatch": True,
            "removed": False,
        }
        for column in COLUMNS
    ]


def sheet_values():
    values = {}
    for column in COLUMNS:
        if " " in column:
            values[column] = "={{ $json['" + column + "'] }}"
        else:
            values[column] = "={{ $json." + column + " }}"
    return values


def groq_body(system: str, user_js: str, max_tokens: int) -> str:
    return (
        "={{ JSON.stringify({ "
        "model: $('Config').first().json.groqModel || 'openai/gpt-oss-20b', "
        "messages: ["
        "{ role: 'system', content: "
        + json.dumps(system)
        + " }, { role: 'user', content: "
        + user_js
        + " }], temperature: 0.2, max_tokens: "
        + str(max_tokens)
        + ", reasoning_effort: 'low' }) }}"
    )


MATCH_SYSTEM = (
    "You score how well a junior AI/ML candidate fits a job. "
    "Candidate: Madiha Shahid, final-year CS student. Skills: Python, JavaScript, "
    "Vertex AI, scikit-learn, PyTorch, OpenCV, React, Node, MySQL, Git, Docker. "
    "She wants a junior role or internship in AI, machine learning, data, or software. "
    'Reply with JSON only: {"match_score":0-100,"summary":"one sentence"}.'
)

VARIANT_SYSTEM = (
    "Choose the resume variant that best fits the job. Reply with JSON only: "
    '{"best_variant":"AI/ML Engineer|Computer Vision Engineer|Full-Stack Software Engineer|Generative AI Engineer","reason":"one sentence"}. '
    "AI/ML = Python, PyTorch, training, deployment. "
    "Computer Vision = OpenCV, images, detection. "
    "Full-Stack = React, Node, Django, APIs. "
    "Generative AI = LLMs, RAG, prompts, Gemini."
)

APPLY_SYSTEM = (
    "Decide how a candidate should apply. Reply with JSON only: "
    '{"method":"email|external_link|dm|phone|form|other|none","email_address":"","email_subject":"","email_body":"","dm_message":"","other_notes":""}. '
    "Use method email only when an address is listed under EMAILS FOUND or clearly written in the excerpt. "
    "Never invent an email address. "
    "For an email, write 3-4 sentences as Madiha Shahid, a final-year CS student and AI/ML engineer, "
    "and include the resume link in the body. Do not say the resume is attached."
)

MATCH_USER = (
    "'JOB: ' + ($json.title || '') + ' at ' + ($json.company || '') + "
    "'\\nLOCATION: ' + ($json.location || '') + '\\nDESCRIPTION:\\n' + ($json.description || '')"
)

VARIANT_USER = (
    "'JOB: ' + ($json.title || '') + ' at ' + ($json.company || '') + "
    "'\\nLOCATION: ' + ($json.location || '') + '\\nDESCRIPTION:\\n' + ($json.description || '')"
)

APPLY_USER = (
    "'JOB: ' + ($json.title || '') + ' at ' + ($json.company || '') + "
    "'\\nLOCATION: ' + ($json.location || '') + "
    "'\\nRESUME VARIANT: ' + ($json.best_variant || '') + "
    "'\\nRESUME LINK: ' + ($json.resume_link || '') + "
    "'\\nEMAILS FOUND IN THE FULL DESCRIPTION: ' + "
    "((Array.isArray($json.emails_found) && $json.emails_found.length) ? $json.emails_found.join(', ') : 'none') + "
    "'\\nDESCRIPTION EXCERPT:\\n' + ($json.description || '')"
)

NORMALIZE = """
const excerptChars = Number($('Config').first().json.descriptionExcerptChars) || 900;
const rows = unwrapRows($input.all().map((item) => item.json));
const jobs = [];
for (const row of rows) {{
  const job = {fn}(row, excerptChars{extra});
  if (job) jobs.push(job);
}}
return jobs.length ? jobs.map((job) => ({{ json: job }})) : [{{ json: {{ _empty: true }} }}];
"""

CURRENT_JOB = """
function currentJob(loopName, waitName) {
  const current = $json || {};
  if (current.title && current.groq_response) {
    const copy = Object.assign({}, current);
    delete copy.groq_response;
    return copy;
  }
  if (current.title && !current.choices) return current;
  try {
    const paired = $(loopName).item.json;
    if (paired && paired.title) return paired;
  } catch (error) {}
  try {
    const waited = $(waitName).item.json;
    if (waited && waited.title) return waited;
  } catch (error) {}
  return null;
}

function jobFields(job) {
  return {
    title: job.title,
    company: job.company,
    location: job.location || '',
    link: job.link || '',
    description: job.description || '',
    emails_found: asEmailList(job.emails_found),
    source: job.source || '',
    region_hint: job.region_hint || '',
    _noJobs: false,
  };
}
"""


def build() -> dict:
    for column in COLUMNS:
        if f"'{column}'" not in LOGIC:
            raise SystemExit(f"logic.js is missing sheet column {column}")

    nodes = []
    links = []

    def add(name, node_type, version, parameters, position, **extra):
        node = {
            "parameters": parameters,
            "type": node_type,
            "typeVersion": version,
            "position": position,
            "id": nid(),
            "name": name,
        }
        node.update(extra)
        nodes.append(node)
        return node

    def link(src, src_index, dst, dst_index=0):
        links.append((src, src_index, dst, dst_index))

    add(
        "Sticky Note",
        "n8n-nodes-base.stickyNote",
        1,
        {
            "content": """## Job Aggregator

Daily at 9:00, or use Manual Trigger.

Paste your Groq, Apify, and Jooble keys into **Config**. They are the three PASTE_ values. Resume links and the Google Sheet id are there too.

### What happens
1. Collect roles from RemoteOK, Jooble, LinkedIn, Indeed, and Rozee.
2. Keep Karachi roles and remote roles that are not limited to another country.
3. Score a capped set, pick a resume variant, then decide how to apply.
4. Append every kept role to the spreadsheet.
5. Send Gmail only when the full job text contains a real address. The resume is linked in the body, not attached.

### Why Gmail and the sheet were skipped
The model only saw the first few hundred characters of each job, so application emails past that cutoff were invisible. Roles the model could not classify were deleted. Gmail and the sheet run only when items arrive, so the execution stopped. Emails are now read from the full text first, and the model only receives a short excerpt. A failed model call no longer deletes the role or stalls the run.

Raise `maxJobsToScore` or `maxEmailsPerRun` in Config if you want a larger daily batch. Keep `descriptionExcerptChars` around 900 so Groq accepts the request.""",
            "height": 620,
            "width": 460,
            "color": 4,
        },
        [0, 180],
    )

    add(
        "Schedule Trigger",
        "n8n-nodes-base.scheduleTrigger",
        1.4,
        {
            "rule": {
                "interval": [
                    {
                        "field": "days",
                        "daysInterval": 1,
                        "triggerAtHour": 9,
                        "triggerAtMinute": 0,
                    }
                ]
            }
        },
        [520, 360],
    )
    add(
        "Manual Trigger",
        "n8n-nodes-base.manualTrigger",
        1,
        {},
        [520, 560],
    )
    add(
        "Config",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForAllItems",
            "jsCode": """
function clean(value) {
  return String(value || '').trim().replace(/^Bearer\\s+/i, '');
}

return [{
  json: {
    groqApiKey: clean('PASTE_GROQ_API_KEY'),
    apifyToken: clean('PASTE_APIFY_TOKEN'),
    joobleApiKey: clean('PASTE_JOOBLE_API_KEY'),
    groqModel: 'openai/gpt-oss-20b',
    spreadsheetId: '"""
            + SPREADSHEET_ID
            + """',
    maxJobsToScore: 12,
    minMatchScore: 50,
    maxEmailsPerRun: 5,
    descriptionExcerptChars: 900,
    resumeLinks: {
      'AI/ML Engineer': 'https://drive.google.com/file/d/1d6iDET10UPl4zrGoHcFJ6BEMZrTM6mp9/view?usp=drive_link',
      'Computer Vision Engineer': 'https://drive.google.com/file/d/1zWA6stGCHLpnx-_7y5HFVcR-cgSJrTVz/view?usp=drive_link',
      'Full-Stack Software Engineer': 'https://drive.google.com/file/d/1ouT2Fl3rSXYwjblX0O6ZjfFWsJLn2x7R/view?usp=drive_link',
      'Generative AI Engineer': 'https://drive.google.com/file/d/1jskW9VaHAYaoyjiGFHudDEIWxLLKqdbI/view?usp=drive_link'
    }
  }
}];
""".strip()
            + "\n",
        },
        [780, 460],
        notes="Replace the three PASTE_ values with your Groq, Apify, and Jooble keys.",
        notesInFlow=True,
    )

    def http(name, position, method, url, json_body=None, timeout=60000, output_field=None, retries=True):
        parameters = {
            "url": url,
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {
                        "name": "User-Agent",
                        "value": "Mozilla/5.0 (compatible; JobAggregator/1.0)",
                    }
                ]
            },
            "options": {"timeout": timeout},
        }
        if method != "GET":
            parameters["method"] = method
        if json_body is not None:
            parameters["sendBody"] = True
            parameters["specifyBody"] = "json"
            parameters["jsonBody"] = json_body
            parameters["headerParameters"]["parameters"].append(
                {"name": "Content-Type", "value": "application/json"}
            )
        if output_field:
            parameters["options"]["response"] = {
                "response": {
                    "responseFormat": "json",
                    "outputPropertyName": output_field,
                }
            }
        extra = {
            "onError": "continueRegularOutput",
            "alwaysOutputData": True,
        }
        if retries:
            extra.update({"retryOnFail": True, "maxTries": 2, "waitBetweenTries": 3000})
        add(name, "n8n-nodes-base.httpRequest", 4.5, parameters, position, **extra)

    http(
        "RemoteOK - Remote Jobs",
        [1120, 80],
        "GET",
        "https://remoteok.com/api",
        timeout=30000,
    )
    http(
        "Jooble - Karachi",
        [1120, 300],
        "POST",
        "={{ 'https://jooble.org/api/' + $('Config').first().json.joobleApiKey }}",
        json.dumps(
            {
                "keywords": "AI Engineer, Machine Learning, Data Engineer, Python Developer, Software Engineer",
                "location": "Karachi, Pakistan",
            }
        ),
        timeout=30000,
    )
    http(
        "Jooble - Remote",
        [1120, 520],
        "POST",
        "={{ 'https://jooble.org/api/' + $('Config').first().json.joobleApiKey }}",
        json.dumps(
            {
                "keywords": "AI Engineer, Machine Learning, Python Developer, remote",
                "location": "",
            }
        ),
        timeout=30000,
    )

    linkedin_body = {
        "autoConvertToAiSearch": True,
        "limitPerSource": 3,
        "scrapeCompany": True,
        "splitByLocation": False,
        "under10Applicants": False,
        "urls": [
            "https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer&location=Karachi%2C%20Pakistan",
            "https://www.linkedin.com/jobs/search/?keywords=Machine%20Learning%20Engineer&location=Karachi%2C%20Pakistan",
            "https://www.linkedin.com/jobs/search/?keywords=Python%20Developer&location=Karachi%2C%20Pakistan",
            "https://www.linkedin.com/jobs/search/?keywords=Junior%20Software%20Developer&location=Karachi%2C%20Pakistan",
            "https://www.linkedin.com/jobs/search/?keywords=AI%20Machine%20Learning%20Engineer&location=Pakistan&f_WT=2",
            "https://www.linkedin.com/jobs/search/?keywords=Python%20Developer%20Remote&location=Pakistan&f_WT=2",
        ],
    }
    http(
        "Apify - LinkedIn",
        [1120, 760],
        "POST",
        "={{ 'https://api.apify.com/v2/acts/curious_coder~linkedin-jobs-scraper/run-sync-get-dataset-items?token=' + encodeURIComponent($('Config').first().json.apifyToken) }}",
        json.dumps(linkedin_body),
        timeout=180000,
        retries=False,
    )

    rozee_page = """
async function pageFunction(context) {
  const jobs = [];
  const seen = new Set();
  const anchors = document.querySelectorAll('a[href*="/job/"]');
  anchors.forEach((anchor) => {
    const title = (anchor.innerText || '').trim();
    const href = anchor.getAttribute('href') || '';
    if (!title || title.length < 4 || seen.has(href)) return;
    if (/login|sign up|job alert/i.test(title)) return;
    seen.add(href);
    const card = anchor.closest('div.job, li, article, tr') || anchor.parentElement;
    const text = card ? card.innerText.trim() : title;
    const lines = text.split('\\n').map((line) => line.trim()).filter(Boolean);
    jobs.push({
      title,
      link: href,
      company: lines.length > 1 ? lines[1] : '',
      location: 'Karachi',
      description: text.slice(0, 5000),
    });
  });
  return { jobs: jobs.slice(0, 20) };
}
""".strip()
    rozee_body = {
        "startUrls": [
            {"url": "https://www.rozee.pk/job/jsearch/q/AI%20Engineer/fc/1184"}
        ],
        "pageFunction": rozee_page,
        "maxPagesPerCrawl": 1,
        "waitUntil": ["networkidle2"],
    }
    http(
        "Apify - Rozee",
        [1120, 1220],
        "POST",
        "={{ 'https://api.apify.com/v2/acts/apify~web-scraper/run-sync-get-dataset-items?token=' + encodeURIComponent($('Config').first().json.apifyToken) }}",
        json.dumps(rozee_body),
        timeout=180000,
        retries=False,
    )

    def normalize(name, position, fn, extra=""):
        source = code(NORMALIZE.format(fn=fn, extra=extra))
        add(
            name,
            "n8n-nodes-base.code",
            2,
            {"mode": "runOnceForAllItems", "jsCode": source},
            position,
            alwaysOutputData=True,
            onError="continueRegularOutput",
        )

    normalize("Normalize - RemoteOK", [1460, 80], "normalizeRemoteOk")
    normalize("Normalize - Jooble Karachi", [1460, 300], "normalizeJooble", ", 'karachi'")
    normalize("Normalize - Jooble Remote", [1460, 520], "normalizeJooble", ", 'remote'")
    normalize("Normalize - LinkedIn", [1460, 760], "normalizeLinkedIn")
    normalize("Normalize - Rozee", [1460, 1220], "normalizeRozee")

    indeed_code = code(
        """
const searches = [
  { position: 'AI Engineer', location: 'Karachi', region_hint: 'karachi' },
  { position: 'Machine Learning Engineer', location: 'Karachi', region_hint: 'karachi' },
  { position: 'Python Developer', location: 'Karachi', region_hint: 'karachi' },
  { position: 'Junior Software Developer', location: 'Karachi', region_hint: 'karachi' },
  { position: 'AI ML Internship', location: 'Karachi', region_hint: 'karachi' },
  { position: 'Software Engineer Remote', location: 'Pakistan', region_hint: 'remote' },
];

try {
  const config = $('Config').first().json;
  const token = String(config.apifyToken || '').trim();
  const excerptChars = Number(config.descriptionExcerptChars) || 900;
  const jobs = [];
  for (const search of searches) {
    try {
      const data = await this.helpers.httpRequest({
        method: 'POST',
        url: 'https://api.apify.com/v2/acts/misceres~indeed-scraper/run-sync-get-dataset-items?token=' + encodeURIComponent(token),
        headers: { 'Content-Type': 'application/json' },
        body: {
          country: 'PK',
          location: search.location,
          maxConcurrency: 1,
          maxItems: 3,
          position: search.position,
          saveOnlyUniqueItems: true,
        },
        json: true,
        timeout: 90000,
      });
      for (const row of unwrapRows([data])) {
        const job = normalizeIndeed(row, excerptChars, search.region_hint);
        if (job) jobs.push(job);
      }
    } catch (searchError) {
      continue;
    }
  }
  if (!jobs.length) return [{ json: { _empty: true } }];
  return jobs.map((job) => ({ json: job }));
} catch (error) {
  return [{ json: { _empty: true } }];
}
"""
    )
    add(
        "Fetch Indeed",
        "n8n-nodes-base.code",
        2,
        {"mode": "runOnceForAllItems", "jsCode": indeed_code},
        [1460, 980],
        alwaysOutputData=True,
        onError="continueRegularOutput",
    )

    add(
        "Merge Sources",
        "n8n-nodes-base.merge",
        3.2,
        {"mode": "append", "numberInputs": 6},
        [1800, 620],
    )
    add(
        "Dedup and Filter",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForAllItems",
            "jsCode": code(
                """
const maxJobs = Number($('Config').first().json.maxJobsToScore) || 12;
const selected = selectJobs($input.all().map((item) => item.json), maxJobs);
if (!selected.jobs.length) {
  return [{ json: { _noJobs: true, send_email: false, reason: selected.reason } }];
}
return selected.jobs.map((job) => ({ json: Object.assign({}, job, { _noJobs: false }) }));
"""
            ),
        },
        [2080, 620],
        alwaysOutputData=True,
    )

    def if_node(name, position, left_value, right_value):
        add(
            name,
            "n8n-nodes-base.if",
            2.2,
            {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "loose",
                        "version": 2,
                    },
                    "conditions": [
                        {
                            "id": nid(),
                            "leftValue": left_value,
                            "rightValue": right_value,
                            "operator": {
                                "type": "string",
                                "operation": "equals",
                            },
                        }
                    ],
                    "combinator": "and",
                },
                "options": {},
            },
            position,
        )

    if_node("IF Has Jobs", [2360, 620], "={{ $json._noJobs ? 'yes' : 'no' }}", "yes")
    add(
        "Format No Jobs",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForAllItems",
            "jsCode": code(
                """
return [{ json: emptySheetRow($json.reason) }];
"""
            ),
        },
        [2640, 360],
    )

    def loop(name, position):
        add(
            name,
            "n8n-nodes-base.splitInBatches",
            3,
            {"batchSize": 1, "options": {}},
            position,
        )

    def wait(name, position):
        add(
            name,
            "n8n-nodes-base.wait",
            1.1,
            {"amount": 3},
            position,
            webhookId=nid(),
        )

    def groq(name, position, system, user_js, max_tokens):
        add(
            name,
            "n8n-nodes-base.httpRequest",
            4.5,
            {
                "method": "POST",
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "Authorization",
                            "value": "={{ 'Bearer ' + String($('Config').first().json.groqApiKey || '').trim().replace(/^Bearer\\s+/i, '') }}",
                        },
                        {"name": "Content-Type", "value": "application/json"},
                    ]
                },
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": groq_body(system, user_js, max_tokens),
                "options": {
                    "timeout": 45000,
                    "response": {
                        "response": {
                            "responseFormat": "json",
                            "outputPropertyName": "groq_response",
                        }
                    },
                },
            },
            position,
            onError="continueRegularOutput",
            alwaysOutputData=True,
            retryOnFail=True,
            maxTries=2,
            waitBetweenTries=4000,
        )

    loop("Loop Over Matching", [2640, 760])
    wait("Wait - Match", [2920, 760])
    groq("Groq - Match CV", [3200, 760], MATCH_SYSTEM, MATCH_USER, 1000)
    add(
        "Attach Match",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForEachItem",
            "jsCode": code(
                CURRENT_JOB
                + """
try {
  const job = currentJob('Loop Over Matching', 'Wait - Match');
  if (!job || !job.title) return { json: { _empty: true } };
  let score = 0;
  let summary = '';
  try {
    const parsed = parseModelJson(groqText($json));
    score = coerceScore(parsed.match_score);
    summary = asText(parsed.summary).slice(0, 240);
  } catch (parseError) {
    score = 0;
  }
  return {
    json: Object.assign(jobFields(job), {
      match_score: score,
      match_summary: summary,
    }),
  };
} catch (error) {
  return { json: { _empty: true } };
}
"""
            ),
        },
        [3480, 760],
        onError="continueRegularOutput",
        alwaysOutputData=True,
    )
    add(
        "Filter by Match Score",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForAllItems",
            "jsCode": code(
                """
const configured = Number($('Config').first().json.minMatchScore);
const result = filterByScore($input.all().map((item) => item.json), Number.isNaN(configured) ? 50 : configured);
if (!result.jobs.length) {
  return [{ json: { _noJobs: true, send_email: false, reason: result.reason } }];
}
return result.jobs.map((job) => ({ json: Object.assign({}, job, { _noJobs: false }) }));
"""
            ),
        },
        [3760, 620],
        alwaysOutputData=True,
    )
    if_node("IF Has Matches", [4040, 620], "={{ $json._noJobs ? 'yes' : 'no' }}", "yes")

    loop("Loop Over Variants", [4320, 760])
    wait("Wait - Variant", [4600, 760])
    groq("Groq - Choose Variant", [4880, 760], VARIANT_SYSTEM, VARIANT_USER, 800)
    add(
        "Attach Variant",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForEachItem",
            "jsCode": code(
                CURRENT_JOB
                + """
try {
  const job = currentJob('Loop Over Variants', 'Wait - Variant');
  if (!job || !job.title) return { json: { _empty: true } };
  const links = ($('Config').first().json.resumeLinks) || {};
  let variant = 'AI/ML Engineer';
  let reason = '';
  try {
    const parsed = parseModelJson(groqText($json));
    variant = coerceVariant(parsed.best_variant);
    reason = asText(parsed.reason).slice(0, 240);
  } catch (parseError) {
    variant = 'AI/ML Engineer';
  }
  return {
    json: Object.assign(jobFields(job), {
      match_score: job.match_score,
      match_summary: job.match_summary || '',
      best_variant: variant,
      variant_reason: reason,
      resume_link: links[variant] || links['AI/ML Engineer'] || '',
    }),
  };
} catch (error) {
  return { json: { _empty: true } };
}
"""
            ),
        },
        [5160, 760],
        onError="continueRegularOutput",
        alwaysOutputData=True,
    )

    loop("Loop Over Applications", [4320, 1040])
    wait("Wait - Application", [4600, 1040])
    groq("Groq - Application Method", [4880, 1040], APPLY_SYSTEM, APPLY_USER, 1600)
    add(
        "Attach Application",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForEachItem",
            "jsCode": code(
                CURRENT_JOB
                + """
try {
  const job = currentJob('Loop Over Applications', 'Wait - Application');
  if (!job || !job.title) return { json: { _empty: true } };
  let parsed = null;
  try {
    parsed = parseModelJson(groqText($json));
  } catch (parseError) {
    parsed = null;
  }
  return { json: decideApplication(job, parsed) };
} catch (error) {
  return { json: { _empty: true } };
}
"""
            ),
        },
        [5160, 1040],
        onError="continueRegularOutput",
        alwaysOutputData=True,
    )
    add(
        "Prepare Sheet Rows",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForAllItems",
            "jsCode": code(
                """
const maxEmails = Number($('Config').first().json.maxEmailsPerRun);
const cap = Number.isNaN(maxEmails) ? 5 : maxEmails;
const jobs = $input.all().map((item) => item.json).filter((job) => job && job.title && !job._empty && !job._noJobs);
if (!jobs.length) {
  const incoming = $input.first();
  const reason = incoming && incoming.json ? incoming.json.reason : '';
  return [{ json: emptySheetRow(reason || 'No applications to log.') }];
}
return applyEmailCap(jobs.map((job) => toTransport(job)), cap).map((row) => ({ json: row }));
"""
            ),
        },
        [5440, 1040],
        alwaysOutputData=True,
    )
    if_node("IF Send Email", [5720, 1040], "={{ $json.send_email ? 'yes' : 'no' }}", "yes")

    loop("Loop Over Emails", [6000, 1240])
    add(
        "Send Application Email",
        "n8n-nodes-base.gmail",
        2.1,
        {
            "sendTo": "={{ $json.email_address }}",
            "subject": "={{ $json.email_subject }}",
            "emailType": "text",
            "message": "={{ $json.email_body }}",
            "options": {"appendAttribution": False},
        },
        [6280, 1240],
        webhookId=nid(),
        onError="continueRegularOutput",
        alwaysOutputData=True,
        credentials={
            "gmailOAuth2": {
                "id": "7nh7s0ZHB1wURzkp",
                "name": "Gmail account",
            }
        },
    )
    add(
        "Mark Email Result",
        "n8n-nodes-base.code",
        2,
        {
            "mode": "runOnceForEachItem",
            "jsCode": """
function sheetFrom(base, emailStatus, status) {
  return {
    Title: base.Title || '',
    Company: base.Company || '',
    Location: base.Location || '',
    'Match Score': base['Match Score'] || '',
    'Best Variant': base['Best Variant'] || '',
    'Resume Link': base['Resume Link'] || '',
    'Job Link': base['Job Link'] || '',
    'Application Method': base['Application Method'] || '',
    'Email Status': emailStatus,
    'DM Message': base['DM Message'] || '',
    Status: status,
  };
}

try {
  const base = $('Loop Over Emails').item.json || {};
  const result = $json || {};
  const errorText = (result.error && (result.error.message || result.error.description)) || result.errorMessage || '';
  const sent = !errorText && !!(result.id || result.threadId || result.messageId);
  if (sent) return { json: sheetFrom(base, 'Sent', 'Email sent') };
  const detail = errorText ? ('Email failed: ' + errorText) : 'Email failed. Check the Gmail credential and the address.';
  return { json: sheetFrom(base, 'Failed', String(detail).slice(0, 300)) };
} catch (error) {
  return {
    json: {
      Title: '(email result unavailable)',
      Company: '',
      Location: '',
      'Match Score': '',
      'Best Variant': '',
      'Resume Link': '',
      'Job Link': '',
      'Application Method': '',
      'Email Status': 'Failed',
      'DM Message': '',
      Status: 'Email step finished but the job row could not be reattached.',
    },
  };
}
""".strip()
            + "\n",
        },
        [6560, 1240],
        onError="continueRegularOutput",
        alwaysOutputData=True,
    )

    add(
        "Log to Sheet",
        "n8n-nodes-base.googleSheets",
        4.5,
        {
            "operation": "append",
            "documentId": {
                "__rl": True,
                "value": SPREADSHEET_ID,
                "mode": "id",
            },
            "sheetName": {
                "__rl": True,
                "value": "Sheet1",
                "mode": "name",
            },
            "columns": {
                "mappingMode": "defineBelow",
                "value": sheet_values(),
                "matchingColumns": [],
                "schema": sheet_schema(),
                "attemptToConvertTypes": False,
                "convertFieldsToString": True,
            },
            "options": {},
        },
        [6840, 760],
        credentials={
            "googleSheetsOAuth2Api": {
                "id": "zgxV7Qxw5482yr2d",
                "name": "Google Sheets account",
            }
        },
    )

    link("Schedule Trigger", 0, "Config")
    link("Manual Trigger", 0, "Config")
    for target in [
        "RemoteOK - Remote Jobs",
        "Jooble - Karachi",
        "Jooble - Remote",
        "Apify - LinkedIn",
        "Fetch Indeed",
        "Apify - Rozee",
    ]:
        link("Config", 0, target)

    link("RemoteOK - Remote Jobs", 0, "Normalize - RemoteOK")
    link("Jooble - Karachi", 0, "Normalize - Jooble Karachi")
    link("Jooble - Remote", 0, "Normalize - Jooble Remote")
    link("Apify - LinkedIn", 0, "Normalize - LinkedIn")
    link("Apify - Rozee", 0, "Normalize - Rozee")

    link("Normalize - Jooble Karachi", 0, "Merge Sources", 0)
    link("Normalize - RemoteOK", 0, "Merge Sources", 1)
    link("Normalize - Jooble Remote", 0, "Merge Sources", 2)
    link("Normalize - LinkedIn", 0, "Merge Sources", 3)
    link("Fetch Indeed", 0, "Merge Sources", 4)
    link("Normalize - Rozee", 0, "Merge Sources", 5)

    link("Merge Sources", 0, "Dedup and Filter")
    link("Dedup and Filter", 0, "IF Has Jobs")
    link("IF Has Jobs", 0, "Format No Jobs")
    link("IF Has Jobs", 1, "Loop Over Matching")
    link("Format No Jobs", 0, "Log to Sheet")

    link("Loop Over Matching", 0, "Filter by Match Score")
    link("Loop Over Matching", 1, "Wait - Match")
    link("Wait - Match", 0, "Groq - Match CV")
    link("Groq - Match CV", 0, "Attach Match")
    link("Attach Match", 0, "Loop Over Matching")

    link("Filter by Match Score", 0, "IF Has Matches")
    link("IF Has Matches", 0, "Format No Jobs")
    link("IF Has Matches", 1, "Loop Over Variants")

    link("Loop Over Variants", 0, "Loop Over Applications")
    link("Loop Over Variants", 1, "Wait - Variant")
    link("Wait - Variant", 0, "Groq - Choose Variant")
    link("Groq - Choose Variant", 0, "Attach Variant")
    link("Attach Variant", 0, "Loop Over Variants")

    link("Loop Over Applications", 0, "Prepare Sheet Rows")
    link("Loop Over Applications", 1, "Wait - Application")
    link("Wait - Application", 0, "Groq - Application Method")
    link("Groq - Application Method", 0, "Attach Application")
    link("Attach Application", 0, "Loop Over Applications")

    link("Prepare Sheet Rows", 0, "IF Send Email")
    link("IF Send Email", 0, "Loop Over Emails")
    link("IF Send Email", 1, "Log to Sheet")
    link("Loop Over Emails", 0, "Log to Sheet")
    link("Loop Over Emails", 1, "Send Application Email")
    link("Send Application Email", 0, "Mark Email Result")
    link("Mark Email Result", 0, "Loop Over Emails")

    connections = {}
    for src, src_index, dst, dst_index in links:
        bucket = connections.setdefault(src, {"main": []})
        while len(bucket["main"]) <= src_index:
            bucket["main"].append([])
        bucket["main"][src_index].append(
            {"node": dst, "type": "main", "index": dst_index}
        )

    workflow = {
        "name": "Job Aggregator",
        "nodes": nodes,
        "pinData": {},
        "connections": connections,
        "active": False,
        "settings": {"executionOrder": "v1"},
        "meta": {"templateCredsSetupCompleted": True},
    }
    validate(workflow)
    return workflow


def validate(workflow: dict) -> None:
    names = [node["name"] for node in workflow["nodes"]]
    if len(names) != len(set(names)):
        raise SystemExit("Duplicate node names")
    known = set(names)
    incoming = {name: 0 for name in names}
    for src, bundle in workflow["connections"].items():
        if src not in known:
            raise SystemExit(f"Connection from unknown node {src}")
        for outputs in bundle.get("main", []):
            for edge in outputs:
                if edge["node"] not in known:
                    raise SystemExit(f"Connection to unknown node {edge['node']}")
                incoming[edge["node"]] += 1
    for node in workflow["nodes"]:
        name = node["name"]
        if name in {"Sticky Note", "Schedule Trigger", "Manual Trigger"}:
            continue
        if incoming[name] == 0:
            raise SystemExit(f"Orphan node: {name}")
        if "jsCode" in node["parameters"]:
            check_syntax(name, node["parameters"]["jsCode"])

    def reachable(start: str) -> set:
        seen = set()
        stack = [start]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            for outputs in workflow["connections"].get(current, {}).get("main", []):
                for edge in outputs:
                    stack.append(edge["node"])
        return seen

    for trigger in ("Schedule Trigger", "Manual Trigger"):
        found = reachable(trigger)
        for required in ("Log to Sheet", "Send Application Email", "Config"):
            if required not in found:
                raise SystemExit(f"{required} is not reachable from {trigger}")

    serialized = json.dumps(workflow)
    for secret_marker in ("gsk_", "apify_api_", "a7ca8ddd-f80a-49ae-967d-3b51d913f9f8"):
        if secret_marker in serialized:
            raise SystemExit("Refusing to write a workflow that still contains an API key")
    if "emails_found" not in serialized:
        raise SystemExit("Application prompt no longer receives extracted emails")
    if "substring(0, 250)" in serialized or "substring(0, 500)" in serialized:
        raise SystemExit("Old description cutoff is still present")
    if workflow["connections"]["Merge Sources"]["main"] == [[]]:
        raise SystemExit("Merge still has no output")


def main() -> None:
    workflow = build()
    destination = ROOT / "Job_Aggregator.json"
    destination.write_text(json.dumps(workflow, indent=2) + "\n")
    print(f"Wrote {destination} ({len(workflow['nodes'])} nodes)")


if __name__ == "__main__":
    main()
