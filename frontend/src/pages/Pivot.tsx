import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api, ROLES } from '../lib/api';

export default function Pivot() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [role, setRole] = useState(ROLES[0].id);

  const submit = async () => {
    if (!userId) return;
    await api.pivot(Number(userId), role);
    navigate(`/roadmap/${userId}?role=${role}`);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Pivot Goal</h1>
      <select className="border p-2 mb-4" value={role} onChange={(e) => setRole(e.target.value)}>
        {ROLES.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
      </select>
      <button className="bg-blue-500 text-white p-2 rounded" onClick={submit}>Pivot</button>
    </div>
  );
}
