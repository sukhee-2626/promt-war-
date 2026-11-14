import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { api } from '../lib/api';

export default function Progress() {
  const { userId } = useParams<{ userId: string }>();
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    if (userId) api.agentLogs(Number(userId)).then((data: any) => setLogs(data)).catch(console.error);
  }, [userId]);

  return (
    <main className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Progress Analytics</h1>
      <div className="card">
        <pre className="text-sm">{JSON.stringify(logs, null, 2)}</pre>
      </div>
    </main>
  );
}
