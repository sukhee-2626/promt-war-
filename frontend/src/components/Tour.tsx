import { useEffect } from 'react';

declare global {
  interface Window {
    introJs: any;
  }
}

export function Tour({ steps }: { steps: any[] }) {
  useEffect(() => {
    // Small delay to ensure DOM elements are rendered
    const timer = setTimeout(() => {
      if (window.introJs) {
        window.introJs().setOptions({ steps }).start();
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [steps]);
  return null;
}
