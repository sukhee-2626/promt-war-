import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

export default function AgentActivity() {
  const { userId, roadmapId } = useParams();
  const [transcript, setTranscript] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`/api/mentor/${userId}/debate/${roadmapId}`).then(res => res.json()),
      fetch(`/api/events/${userId}/logs`).then(res => res.json())
    ])
      .then(([debate, logs]) => {
        setTranscript(debate);
        setLogs(logs);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setLoading(false);
      });
  }, [userId, roadmapId]);

  if (loading) return <div className="p-8">Loading logs...</div>;

  return (
    <div className="p-8 grid grid-cols-2 gap-8">
      <div>
        <h1 className="text-2xl font-bold mb-4">Debate Log</h1>
        <div className="flex flex-col gap-4">
          {transcript.map((item, i) => (
            <div key={i} className="p-4 border rounded shadow-sm">
              <strong className="block text-sm text-gray-500">
                {item.speaker} - Round {item.round}
              </strong>
              <p className="mt-1">{item.content}</p>
              {item.nodes && <pre className="text-xs bg-gray-100 p-2 mt-2">{JSON.stringify(item.nodes, null, 2)}</pre>}
              {item.issues && <pre className="text-xs bg-red-50 p-2 mt-2">{JSON.stringify(item.issues, null, 2)}</pre>}
            </div>
          ))}
        </div>
      </div>
      <div>
        <h1 className="text-2xl font-bold mb-4">Event Logs</h1>
        <div className="flex flex-col gap-4">
          {logs.map((log, i) => (
            <div key={i} className="p-4 border rounded shadow-sm bg-gray-50">
              <strong className="block text-sm text-gray-500">{log.agent} - {log.created_at}</strong>
              <div className="mt-2 text-xs">
                <p><strong>Input:</strong> {JSON.stringify(log.input)}</p>
                <p className="mt-1"><strong>Output:</strong> {JSON.stringify(log.output)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
