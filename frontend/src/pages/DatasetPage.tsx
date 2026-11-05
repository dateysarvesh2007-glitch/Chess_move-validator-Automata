import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Play, 
  CheckCircle2, 
  XCircle, 
  Upload, 
  BarChart3, 
  Filter 
} from 'lucide-react';
import { 
  fetchDatasetSamples, 
  runDatasetValidation 
} from '../services/api';
import type { 
  DatasetSample, 
  DatasetValidateResponse, 
  DatasetGameResult 
} from '../services/api';

export const DatasetPage: React.FC = () => {
  const [samples, setSamples] = useState<DatasetSample[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [running, setRunning] = useState<boolean>(false);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'legal' | 'illegal'>('all');
  const [customPgn, setCustomPgn] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'samples' | 'custom'>('samples');
  const [validationResult, setValidationResult] = useState<DatasetValidateResponse | null>(null);
  const [selectedGameResult, setSelectedGameResult] = useState<DatasetGameResult | null>(null);

  useEffect(() => {
    loadSamples();
  }, []);

  const loadSamples = async () => {
    try {
      setLoading(true);
      const data = await fetchDatasetSamples();
      setSamples(data.samples);
    } catch (err) {
      console.error('Failed to load dataset samples', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAll = async (type: 'all' | 'legal' | 'illegal') => {
    try {
      setRunning(true);
      setValidationResult(null);
      setSelectedGameResult(null);
      const res = await runDatasetValidation({ test_type: type });
      setValidationResult(res);
      if (res.games.length > 0) {
        setSelectedGameResult(res.games[0]);
      }
    } catch (err) {
      console.error('Validation failed', err);
    } finally {
      setRunning(false);
    }
  };

  const handleRunSingleSample = async (sampleId: string) => {
    try {
      setRunning(true);
      setValidationResult(null);
      setSelectedGameResult(null);
      const res = await runDatasetValidation({ sample_id: sampleId });
      setValidationResult(res);
      if (res.games.length > 0) {
        setSelectedGameResult(res.games[0]);
      }
    } catch (err) {
      console.error('Failed to validate single sample', err);
    } finally {
      setRunning(false);
    }
  };

  const handleRunCustomPgn = async () => {
    if (!customPgn.trim()) return;
    try {
      setRunning(true);
      setValidationResult(null);
      setSelectedGameResult(null);
      const res = await runDatasetValidation({ pgn_content: customPgn });
      setValidationResult(res);
      if (res.games.length > 0) {
        setSelectedGameResult(res.games[0]);
      }
    } catch (err: any) {
      alert(err.message || 'Custom PGN parsing failed');
    } finally {
      setRunning(false);
    }
  };

  const filteredSamples = samples.filter((s) => {
    if (selectedFilter === 'all') return true;
    return s.category === selectedFilter;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
            <Database className="w-4 h-4" />
            <span>Dataset Verification Suite</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Lichess Database & Negative Test Benchmark
          </h1>
          <p className="text-sm text-slate-400 mt-2 max-w-3xl leading-relaxed">
            Batch-validate full chess game sequences from the open Lichess database and stress-test the four validation layers
            against deliberate illegal move scenarios.
          </p>
        </div>

        {/* Dataset Attribution Badge */}
        <div className="bg-[#111a2e] border border-slate-800 p-3.5 rounded-xl text-xs space-y-1 shrink-0">
          <div className="flex items-center justify-between text-slate-300 font-semibold">
            <span>Lichess Open Database</span>
            <span className="text-[10px] uppercase font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
              CC0 License
            </span>
          </div>
          <p className="text-[11px] text-slate-500 max-w-xs">
            Curated subset of master games and negative edge cases. No large PGN downloads or client-side engine reliance.
          </p>
        </div>
      </div>

      {/* Mode Switcher: Preloaded Samples vs Custom PGN Upload */}
      <div className="flex items-center space-x-3 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab('samples')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'samples'
              ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
              : 'bg-[#111a2e] text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <Database className="w-3.5 h-3.5" />
          <span>Curated Benchmark Library</span>
        </button>

        <button
          onClick={() => setActiveTab('custom')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'custom'
              ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
              : 'bg-[#111a2e] text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload / Paste Custom PGN</span>
        </button>
      </div>

      {/* TAB 1: SAMPLES LIBRARY */}
      {activeTab === 'samples' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 bg-[#111a2e] p-4 rounded-xl border border-slate-800">
            {/* Filter Buttons */}
            <div className="flex items-center space-x-2 text-xs">
              <span className="text-slate-400 font-bold uppercase mr-1 flex items-center space-x-1">
                <Filter className="w-3.5 h-3.5" />
                <span>Filter:</span>
              </span>
              {(['all', 'legal', 'illegal'] as const).map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedFilter(cat)}
                  className={`px-3 py-1.5 rounded-lg font-semibold uppercase text-[11px] transition-colors ${
                    selectedFilter === cat
                      ? 'bg-slate-700 text-white'
                      : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {cat === 'all' ? 'All Games' : cat === 'legal' ? 'Legal Master Games' : 'Negative Test Cases'}
                </button>
              ))}
            </div>

            {/* Batch Run Button */}
            <button
              onClick={() => handleRunAll(selectedFilter)}
              disabled={running}
              className="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold text-xs flex items-center space-x-2 transition-all shadow-md shadow-amber-500/20"
            >
              {running ? (
                <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              ) : (
                <Play className="w-3.5 h-3.5 fill-current" />
              )}
              <span>Run Validation Batch</span>
            </button>
          </div>

          {/* Sample Games Cards Grid */}
          {loading ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              Loading benchmark library...
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredSamples.map((sample) => (
                <div
                  key={sample.id}
                  className="bg-[#111a2e]/70 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-slate-700 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${
                        sample.category === 'legal'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-red-500/10 text-red-400 border-red-500/30'
                      }`}>
                        {sample.category === 'legal' ? 'Legal Benchmark' : 'Negative Test Case'}
                      </span>
                      <span className="text-xs font-mono text-slate-500">{sample.move_count} moves</span>
                    </div>

                    <h3 className="text-sm font-bold text-white line-clamp-1">{sample.title}</h3>
                    <div className="text-xs text-slate-400 mt-1">
                      {sample.white} vs {sample.black} ({sample.result})
                    </div>
                    <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                      {sample.description}
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                    <span className="text-[11px] font-mono text-slate-500">{sample.id}</span>
                    <button
                      onClick={() => handleRunSingleSample(sample.id)}
                      disabled={running}
                      className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-400 font-semibold text-xs flex items-center space-x-1 transition-colors"
                    >
                      <span>Test Game</span>
                      <Play className="w-3 h-3 fill-current" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: CUSTOM PGN INPUT */}
      {activeTab === 'custom' && (
        <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4">
          <div>
            <h3 className="text-lg font-bold text-white">Paste Custom PGN Game</h3>
            <p className="text-xs text-slate-400 mt-1">
              Paste standard PGN format text with headers and moves. The engine parses tags, strips annotations, and validates move legality.
            </p>
          </div>

          <textarea
            rows={8}
            value={customPgn}
            onChange={(e) => setCustomPgn(e.target.value)}
            placeholder={`[Event "Custom Game"]\n[White "Player1"]\n[Black "Player2"]\n[Result "1-0"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4 1-0`}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-xl p-4 text-xs font-mono text-white placeholder:text-slate-600 focus:outline-none focus:border-amber-500/80"
          />

          <div className="flex justify-end">
            <button
              onClick={handleRunCustomPgn}
              disabled={running || !customPgn.trim()}
              className="px-6 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold text-xs flex items-center space-x-2 transition-all shadow-md shadow-amber-500/20"
            >
              {running ? (
                <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              ) : (
                <Play className="w-3.5 h-3.5 fill-current" />
              )}
              <span>Validate Uploaded PGN</span>
            </button>
          </div>
        </div>
      )}

      {/* VALIDATION RESULTS REPORT SECTION */}
      {validationResult && (
        <section className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-8 shadow-2xl animate-fadeIn">
          {/* Summary KPI Cards */}
          <div>
            <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 uppercase tracking-wider mb-3">
              <BarChart3 className="w-4 h-4" />
              <span>Validation Outcome & Benchmark Statistics</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-6">
              {validationResult.dataset_name}
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-xs text-slate-400">Total Games Tested</div>
                <div className="text-2xl font-bold text-white mt-1">{validationResult.total_games}</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-xs text-slate-400">Accepted Games (Legal)</div>
                <div className="text-2xl font-bold text-emerald-400 mt-1">{validationResult.accepted_games}</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-xs text-slate-400">Rejected Games (Illegal)</div>
                <div className="text-2xl font-bold text-red-400 mt-1">{validationResult.rejected_games}</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-xs text-slate-400">Total Moves Evaluated</div>
                <div className="text-2xl font-bold text-amber-400 mt-1">{validationResult.total_moves}</div>
              </div>
            </div>
          </div>

          {/* Per-Game Detailed Outcomes Table */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Per-Game Validation Diagnostic Table
            </h4>

            <div className="overflow-x-auto rounded-xl border border-slate-800">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="p-3">Game Title</th>
                    <th className="p-3">Category</th>
                    <th className="p-3">Moves Processed</th>
                    <th className="p-3">Engine Verdict</th>
                    <th className="p-3">Failure Diagnostics</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                  {validationResult.games.map((g) => (
                    <tr
                      key={g.id}
                      onClick={() => setSelectedGameResult(g)}
                      className={`cursor-pointer transition-colors ${
                        selectedGameResult?.id === g.id ? 'bg-amber-500/10' : 'hover:bg-slate-900/40'
                      }`}
                    >
                      <td className="p-3 font-semibold text-white">{g.title}</td>
                      <td className="p-3">
                        <span className="capitalize text-slate-400">{g.metadata?.Category || 'Legal'}</span>
                      </td>
                      <td className="p-3 text-slate-300">
                        {g.processed_moves} / {g.total_moves}
                      </td>
                      <td className="p-3">
                        {g.status === 'ACCEPTED' ? (
                          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 font-bold border border-emerald-500/30">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>ACCEPTED</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-red-500/15 text-red-400 font-bold border border-red-500/30">
                            <XCircle className="w-3 h-3" />
                            <span>REJECTED</span>
                          </span>
                        )}
                      </td>
                      <td className="p-3 text-slate-400 max-w-xs truncate">
                        {g.reason}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Selected Game Deep Dive Drawer */}
          {selectedGameResult && (
            <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                  Selected Game Diagnostic
                </span>
                <span className="text-xs font-mono text-slate-400">{selectedGameResult.id}</span>
              </div>
              <h4 className="text-base font-bold text-white">{selectedGameResult.title}</h4>
              <p className="text-xs text-slate-300">
                <strong className="text-amber-400">Engine Verdict: </strong> {selectedGameResult.reason}
              </p>
              {selectedGameResult.failing_move && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs font-mono text-red-300">
                  Failing Move: <strong>{selectedGameResult.failing_move}</strong> (Halted at move {selectedGameResult.processed_moves + 1})
                </div>
              )}
            </div>
          )}
        </section>
      )}
    </div>
  );
};
