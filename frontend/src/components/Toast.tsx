import { useEffect } from 'react';
import { AlertCircle } from 'lucide-react';

export const Toast = ({message, onClose}: {message: string, onClose: () => void}) => {
  useEffect(() => { const t = setTimeout(onClose, 3000); return () => clearTimeout(t); }, [onClose]);
  return <div className="fixed bottom-4 right-4 p-4 bg-gray-800 text-white rounded shadow z-50 flex items-center gap-2"><AlertCircle size={18}/>{message}</div>;
}
