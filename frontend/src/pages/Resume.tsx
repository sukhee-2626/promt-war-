import { useState } from 'react';
import { useParams } from 'react-router-dom';

export default function Resume() {
  const { userId } = useParams<{ userId: string }>();
  const [resumeText, setResumeText] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);

  const handleOptimize = async () => {
    // This would ideally call an ATS optimization agent endpoint
    // Placeholder for now
    setAnalysis({
      score: 75,
      matchedKeywords: ['Python', 'SQL', 'Git'],
      missingKeywords: ['Docker', 'Kubernetes', 'AWS'],
    });
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Resume ATS Optimization</h1>
      <textarea
        className="w-full h-64 p-4 border rounded"
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
        placeholder="Paste your resume here..."
      />
      <button
        onClick={handleOptimize}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Optimize Resume
      </button>

      {analysis && (
        <div className="mt-8 p-4 border rounded">
          <h2 className="text-xl font-bold">ATS Score: {analysis.score}%</h2>
          <div className="mt-4">
            <h3 className="font-semibold">Matched Keywords:</h3>
            <ul className="list-disc ml-5">
              {analysis.matchedKeywords.map((k: string) => <li key={k}>{k}</li>)}
            </ul>
          </div>
          <div className="mt-4">
            <h3 className="font-semibold">Missing Keywords:</h3>
            <ul className="list-disc ml-5 text-red-600">
              {analysis.missingKeywords.map((k: string) => <li key={k}>{k}</li>)}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
