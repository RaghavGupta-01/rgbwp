import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'decision' | 'accuracy'>('decision');
  const [cutoffTime] = useState<string>('09:00');

  return (
    <Layout
      activeTab={activeTab}
      onTabChange={setActiveTab}
      cutoffTime={cutoffTime}
    >
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center text-slate-500">
        {activeTab === 'decision' ? (
          <div>
            <h2 className="text-lg font-semibold text-slate-800">Tomorrow's Decision View</h2>
            <p className="text-sm mt-1">Controls and charts will render here.</p>
          </div>
        ) : (
          <div>
            <h2 className="text-lg font-semibold text-slate-800">Forecast Accuracy Analytics</h2>
            <p className="text-sm mt-1">Accuracy KPIs and distribution charts will render here.</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
};

export default App;
