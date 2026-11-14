import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api, fmtRole, ROLES } from '../lib/api';

export default function CareerMatch() {
  const { userId } = useParams<{ userId: string }>();
  const [match, setMatch] = useState<any>(null);
  const [role, setRole] = useState<string>('');

  useEffect(() => {
    if (userId) {
      api.match(parseInt(userId), role || undefined).then(setMatch).catch(console.error);
    }
  }, [userId, role]);

  if (!match) return <div className="p-8">Loading match analysis...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Career Match</h1>
      <select className="mb-4 p-2 border" onChange={e => setRole(e.target.value)} value={role}>
        <option value="">Select a role (optional)</option>
        {ROLES.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
      </select>
      <div className="bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold">{match.role_name || 'Match Analysis'}</h2>
        <p className="mt-2 text-gray-700">{match.analysis || 'No detailed analysis available.'}</p>
        {match.score && <p className="mt-4 font-bold">Match Score: {match.score}%</p>}
      </div>
    </div>
  );
}
