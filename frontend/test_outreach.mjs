import assert from 'node:assert';
import fs from 'node:fs';

// Verify Outreach.tsx exists and exports default function Outreach
const code = fs.readFileSync('./src/pages/Outreach.tsx', 'utf-8');
assert(code.includes('export default function Outreach'), 'Must export default function Outreach');
assert(code.includes('generateOutreach'), 'Must include generateOutreach logic');
assert(code.includes('Cold Recruiter Email') || code.includes('emailSubject'), 'Must support email generation');
assert(code.includes('LinkedIn') || code.includes('linkedinMessage'), 'Must support LinkedIn generation');

// Extract and test generateOutreach logic directly
const funcMatch = code.match(/export function generateOutreach[\s\S]*?\n\}/);
assert(funcMatch, 'generateOutreach function must be extractable');

// Clean TS types for node eval
const jsFunc = funcMatch[0]
  .replace(/: OutreachForm/, '')
  .replace(/: OutreachResult/, '')
  .replace('export ', '');

const generateOutreach = new Function('form', `${jsFunc}; return generateOutreach(form);`);

const result = generateOutreach({
  candidateName: 'Alice',
  targetRole: 'Backend Engineer',
  companyName: 'Acme Corp',
  recruiterName: 'Bob',
  keySkills: 'Python, FastAPI',
  portfolioUrl: 'https://alice.dev',
});

assert.strictEqual(result.emailSubject, 'Backend Engineer Role - Alice');
assert(result.emailBody.includes('Acme Corp'));
assert(result.emailBody.includes('Hi Bob'));
assert(result.emailBody.includes('https://alice.dev'));
assert(result.linkedinMessage.includes('Bob'));
assert(result.linkedinMessage.includes('Acme Corp'));
assert(result.linkedinMessage.length <= 300, 'LinkedIn note must be <= 300 chars');

console.log('Outreach self-check passed: All assertions verified.');
