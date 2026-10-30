import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { DecisionView } from './pages/DecisionView';
import { AccuracyView } from './pages/AccuracyView';

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
  const [dateFrom, setDateFrom] = useState<string>('2026-01-02');
  const [dateTo, setDateTo] = useState<string>('2026-02-01');
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
        <AccuracyView
          dateFrom={dateFrom}
          onDateFromChange={setDateFrom}
          dateTo={dateTo}
          onDateToChange={setDateTo}
          cutoffTime={cutoffTime}
          onCutoffTimeChange={setCutoffTime}
        />
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
