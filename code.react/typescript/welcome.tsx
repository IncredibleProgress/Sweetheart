// Maintenance App Refactory

import React from 'react';
import ReactDOM from 'react-dom/client';

function App(): React.JSX.Element {
  return (
    <div>
      <button className="rounded bg-blue-500 px-4 py-2 font-bold text-white hover:bg-blue-700">
        Hello, Tailwind!
      </button>
    </div>
  );
}

const app: HTMLElement | null = document.getElementById('ReactApp');
ReactDOM.createRoot(app!).render(<App />);
