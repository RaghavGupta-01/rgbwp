import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { DecisionView } from './pages/DecisionView';

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
  const [deliveryDate, setDeliveryDate] = useState<string>('2026-01-02');
  const [cutoffTime, setCutoffTime] = useState<string>('09:00');

  return (
    <Layout
      activeTab={activeTab}
      onTabChange={setActiveTab}
      cutoffTime={cutoffTime}
    >
      {activeTab === 'decision' ? (
        <DecisionView
          deliveryDate={deliveryDate}
          onDeliveryDateChange={setDeliveryDate}
          cutoffTime={cutoffTime}
          onCutoffTimeChange={setCutoffTime}
        />
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center text-slate-500">
          <h2 className="text-lg font-semibold text-slate-800">Forecast Accuracy Analytics</h2>
          <p className="text-sm mt-1">Accuracy KPIs and distribution charts will render here.</p>
        </div>
      )}
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
