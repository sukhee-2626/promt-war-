import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

interface Question {
  text: string;
  options: string[];
  correct_index: number;
}

export default function Assess() {
  const { userId, skillId } = useParams<{ userId: string; skillId: string }>();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:8000/assess/${userId}/${skillId}`)
      .then(res => res.json())
      .then(data => {
        setQuestions(data.questions);
        setAnswers(new Array(data.questions.length).fill(-1));
        setLoading(false);
      });
  }, [userId, skillId]);

  const submit = () => {
    fetch(`http://localhost:8000/assess/${userId}/${skillId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    }).then(res => res.json()).then(console.log);
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4">Assessment: {skillId}</h1>
      {questions.map((q, qIdx) => (
        <div key={qIdx} className="mb-6">
          <p className="font-medium">{q.text}</p>
          {q.options.map((opt, oIdx) => (
            <button
              key={oIdx}
              className={`block w-full p-2 mt-2 border rounded ${answers[qIdx] === oIdx ? 'bg-blue-100' : ''}`}
              onClick={() => setAnswers(prev => prev.map((a, i) => i === qIdx ? oIdx : a))}
            >
              {opt}
            </button>
          ))}
        </div>
      ))}
      <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={submit}>Submit</button>
    </div>
  );
}
