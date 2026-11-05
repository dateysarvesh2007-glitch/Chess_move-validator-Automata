import { useState } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { LandingPage } from './pages/LandingPage';
import { ValidatorPage } from './pages/ValidatorPage';
import { AutomataPage } from './pages/AutomataPage';
import { DatasetPage } from './pages/DatasetPage';
import { AboutPage } from './pages/AboutPage';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('landing');

  return (
    <div className="min-h-screen bg-[#0a0f1d] text-slate-100 flex flex-col selection:bg-amber-500/30 selection:text-amber-300">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1">
        {activeTab === 'landing' && (
          <LandingPage
            onStartValidating={() => setActiveTab('validator')}
            onExploreAutomata={() => setActiveTab('automata')}
            onOpenDataset={() => setActiveTab('dataset')}
          />
        )}

        {activeTab === 'validator' && <ValidatorPage />}

        {activeTab === 'automata' && <AutomataPage />}

        {activeTab === 'dataset' && <DatasetPage />}

        {activeTab === 'about' && <AboutPage />}
      </main>

      <Footer />
    </div>
  );
}

export default App;
