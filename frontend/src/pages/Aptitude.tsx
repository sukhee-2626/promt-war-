import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function Aptitude() {
  const { aptitudeId } = useParams<{ aptitudeId: string }>();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<any[]>([]);
  const [answers, setAnswers] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/aptitude/${aptitudeId}`)
      .then(res => res.json())
      .then(data => {
        setQuestions(data.questions);
        setAnswers(new Array(data.questions.length).fill(-1));
        setLoading(false);
      });
  }, [aptitudeId]);

  const submit = () => {
    fetch(`/api/aptitude/${aptitudeId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    }).then(() => navigate('/dashboard'));
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Aptitude Test</h1>
      {questions.map((q, qIdx) => (
        <div key={qIdx} className="mb-8">
          <p className="text-lg font-medium mb-4">{q.text}</p>
          {q.options.map((opt: string, oIdx: number) => (
            <button
              key={oIdx}
              className={`block w-full text-left p-4 mb-2 border rounded ${answers[qIdx] === oIdx ? 'bg-blue-600 text-white' : 'hover:bg-gray-50'}`}
              onClick={() => setAnswers(prev => prev.map((a, i) => i === qIdx ? oIdx : a))}
            >
              {opt}
            </button>
          ))}
        </div>
      ))}
      <button className="w-full py-3 bg-blue-600 text-white rounded font-bold" onClick={submit}>Finish</button>
    </div>
  );
}
