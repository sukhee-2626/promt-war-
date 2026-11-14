import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Copy, Check, Mail, Linkedin, Sparkles } from 'lucide-react';
import { api, fmtRole } from '../lib/api';

export interface OutreachForm {
  candidateName: string;
  targetRole: string;
  companyName: string;
  recruiterName: string;
  keySkills: string;
  portfolioUrl: string;
}

export interface OutreachResult {
  emailSubject: string;
  emailBody: string;
  linkedinMessage: string;
}

export function generateOutreach(form: OutreachForm): OutreachResult {
  const candidate = form.candidateName.trim() || 'Candidate';
  const role = form.targetRole.trim() || 'Software Engineer';
  const company = form.companyName.trim() || 'your company';
  const recruiter = form.recruiterName.trim() || 'Hiring Team';
  const skills = form.keySkills.trim() || 'software engineering';
  const portfolio = form.portfolioUrl.trim();

  // ponytail: client-side template generator; upgrade to backend LLM streaming when Ollama/Groq endpoint is wired to /outreach.
  const emailSubject = `${role} Role - ${candidate}`;
  const portfolioLine = portfolio ? `\n\nPortfolio: ${portfolio}` : '';
  const emailBody = `Hi ${recruiter},

I noticed ${company} is looking for a ${role}. With hands-on experience in ${skills}, I believe my background aligns well with your team's goals.${portfolioLine}

Would you be open to a brief 10-minute chat this week?

Best regards,
${candidate}`;

  const linkedinMessage = `Hi ${recruiter}, noticed your talent search for ${company}. I'm a ${role} specializing in ${skills}. Would love to connect!`;

  return { emailSubject, emailBody, linkedinMessage };
}

export default function Outreach() {
  const { userId } = useParams<{ userId: string }>();
  const [form, setForm] = useState<OutreachForm>({
    candidateName: '',
    targetRole: 'Full Stack Developer',
    companyName: '',
    recruiterName: 'Hiring Team',
    keySkills: '',
    portfolioUrl: '',
  });

  const [result, setResult] = useState<OutreachResult | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;
    api.getProfile(Number(userId))
      .then((p: any) => {
        if (!p) return;
        setForm(prev => ({
          ...prev,
          candidateName: p.name || prev.candidateName,
          targetRole: p.goal_role ? fmtRole(p.goal_role) : prev.targetRole,
          keySkills: Array.isArray(p.skills) && p.skills.length > 0
            ? p.skills.map((s: any) => s.skill_id || s.name).slice(0, 4).join(', ')
            : prev.keySkills,
        }));
      })
      .catch(console.error);
  }, [userId]);

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    const res = generateOutreach(form);
    setResult(res);
    if (userId) {
      api.postEvent(Number(userId), 'outreach', {
        company: form.companyName,
        role: form.targetRole,
      }).catch(console.error);
    }
  };

  const copyToClipboard = async (text: string, key: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const charCount = result ? result.linkedinMessage.length : 0;

  return (
    <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Sparkles className="text-indigo-400" size={28} />
          Recruiter Outreach Generator
        </h1>
        <p className="text-gray-400 mt-1">
          Generate high-converting recruiter emails and LinkedIn connection notes.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <form onSubmit={handleGenerate} className="card space-y-4">
          <h2 className="text-xl font-semibold text-gray-200">Target Details</h2>

          <div>
            <label className="block text-xs font-semibold text-gray-400 mb-1">CANDIDATE NAME</label>
            <input
              type="text"
              className="input"
              value={form.candidateName}
              onChange={e => setForm({ ...form, candidateName: e.target.value })}
              placeholder="e.g. Alex Chen"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 mb-1">TARGET ROLE</label>
            <input
              type="text"
              className="input"
              value={form.targetRole}
              onChange={e => setForm({ ...form, targetRole: e.target.value })}
              placeholder="e.g. Full Stack Developer"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">COMPANY NAME *</label>
              <input
                type="text"
                required
                className="input"
                value={form.companyName}
                onChange={e => setForm({ ...form, companyName: e.target.value })}
                placeholder="e.g. Stripe"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">RECRUITER / HIRING MANAGER</label>
              <input
                type="text"
                className="input"
                value={form.recruiterName}
                onChange={e => setForm({ ...form, recruiterName: e.target.value })}
                placeholder="e.g. Sarah"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 mb-1">KEY SKILLS (COMMA-SEPARATED)</label>
            <input
              type="text"
              className="input"
              value={form.keySkills}
              onChange={e => setForm({ ...form, keySkills: e.target.value })}
              placeholder="e.g. React, TypeScript, Python, FastAPI"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 mb-1">PORTFOLIO / GITHUB URL</label>
            <input
              type="url"
              className="input"
              value={form.portfolioUrl}
              onChange={e => setForm({ ...form, portfolioUrl: e.target.value })}
              placeholder="https://github.com/..."
            />
          </div>

          <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2 mt-2">
            <Sparkles size={18} />
            Generate Messages
          </button>
        </form>

        <div className="space-y-6">
          {!result ? (
            <div className="card h-full min-h-[360px] flex flex-col items-center justify-center text-center p-8 text-gray-400">
              <Mail className="text-gray-600 mb-3" size={40} />
              <p className="font-medium text-gray-300">No messages generated yet</p>
              <p className="text-sm mt-1">Fill target company and click Generate Messages.</p>
            </div>
          ) : (
            <>
              {/* Cold Email */}
              <div className="card space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
                    <Mail size={18} />
                    Cold Recruiter Email
                  </div>
                  <button
                    onClick={() => copyToClipboard(`Subject: ${result.emailSubject}\n\n${result.emailBody}`, 'email')}
                    className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
                  >
                    {copiedKey === 'email' ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                    {copiedKey === 'email' ? 'Copied' : 'Copy Full Email'}
                  </button>
                </div>

                <div className="bg-gray-800/80 rounded-xl p-3 border border-gray-700/60">
                  <div className="text-xs text-gray-400 mb-1 font-mono">SUBJECT</div>
                  <div className="text-sm text-gray-200 font-medium select-all">{result.emailSubject}</div>
                </div>

                <div className="bg-gray-800/80 rounded-xl p-3 border border-gray-700/60">
                  <div className="text-xs text-gray-400 mb-1 font-mono">BODY</div>
                  <pre className="text-sm text-gray-200 whitespace-pre-wrap font-sans select-all">{result.emailBody}</pre>
                </div>
              </div>

              {/* LinkedIn Note */}
              <div className="card space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-blue-400 font-semibold text-sm">
                    <Linkedin size={18} />
                    LinkedIn Connection Note
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-mono ${charCount <= 300 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {charCount}/300
                    </span>
                    <button
                      onClick={() => copyToClipboard(result.linkedinMessage, 'linkedin')}
                      className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
                    >
                      {copiedKey === 'linkedin' ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                      {copiedKey === 'linkedin' ? 'Copied' : 'Copy Note'}
                    </button>
                  </div>
                </div>

                <div className="bg-gray-800/80 rounded-xl p-3 border border-gray-700/60">
                  <pre className="text-sm text-gray-200 whitespace-pre-wrap font-sans select-all">{result.linkedinMessage}</pre>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
