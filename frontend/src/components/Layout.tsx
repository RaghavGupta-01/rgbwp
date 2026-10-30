import React, { useState } from 'react';
import { Wind, BarChart3, Clock, Info, ShieldCheck } from 'lucide-react';

interface LayoutProps {
  activeTab: 'decision' | 'accuracy';
  onTabChange: (tab: 'decision' | 'accuracy') => void;
  cutoffTime: string;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({
  activeTab,
  onTabChange,
  cutoffTime,
  children,
}) => {
  const [showInfo, setShowInfo] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Branding & Logo */}
            <div className="flex items-center space-x-3">
              <div className="bg-sky-600 p-2 rounded-lg text-white shadow-sm flex items-center justify-center">
                <Wind className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h1 className="text-lg font-bold tracking-tight text-slate-900 leading-none">
                  GB Wind Forecast Portal
                </h1>
                <p className="text-xs text-slate-500 mt-1 flex items-center space-x-1">
                  <span>Day-Ahead Decision Desk</span>
                  <span>•</span>
                  <span className="text-slate-600 font-medium">Elexon BMRS (GB National Wind)</span>
                </p>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="flex space-x-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
              <button
                type="button"
                onClick={() => onTabChange('decision')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-sm font-medium transition-all ${
                  activeTab === 'decision'
                    ? 'bg-white text-sky-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                }`}
              >
                <Clock className="w-4 h-4" />
                <span>Tomorrow's View</span>
              </button>
              <button
                type="button"
                onClick={() => onTabChange('accuracy')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-sm font-medium transition-all ${
                  activeTab === 'accuracy'
                    ? 'bg-white text-sky-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span>Forecast Accuracy</span>
              </button>
            </nav>

            {/* Status & Info Badge */}
            <div className="hidden md:flex items-center space-x-3">
              <div className="flex items-center space-x-1.5 bg-slate-100 px-3 py-1 rounded-full text-xs text-slate-700 border border-slate-200">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span className="font-medium">Active Cutoff: {cutoffTime} UK (UTC)</span>
              </div>
              <button
                type="button"
                onClick={() => setShowInfo(!showInfo)}
                className="p-1.5 text-slate-500 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
                title="How to read this portal"
              >
                <Info className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Collapsible Info Drawer */}
        {showInfo && (
          <div className="bg-sky-50 border-t border-sky-100 px-4 py-3 sm:px-6 lg:px-8 text-xs text-sky-900">
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div className="flex items-start space-x-2">
                <ShieldCheck className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold">Sign Convention:</span> Error = Forecast − Actual (MW).
                  Positive error (+MW) means over-forecast (power under-procured).
                  Negative error (−MW) means under-forecast (wind exceeded forecast).
                </div>
              </div>
              <div className="text-slate-500">
                Decision Range: Jan 2026 (Delivery: 2026-01-02 to 2026-02-01)
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        <p>GB Wind Forecast Decision Portal • Sourced exclusively from Elexon BMRS (FUELHH & WINDFOR streams)</p>
      </footer>
    </div>
  );
};
