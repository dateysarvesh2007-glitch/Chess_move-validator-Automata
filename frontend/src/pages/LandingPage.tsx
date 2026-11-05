import React from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  Database, 
  ArrowRight, 
  CheckCircle2, 
  Lock, 
  GitBranch, 
  History, 
  Sparkles,
  Layers
} from 'lucide-react';

interface LandingPageProps {
  onStartValidating: () => void;
  onExploreAutomata: () => void;
  onOpenDataset: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartValidating,
  onExploreAutomata,
  onOpenDataset,
}) => {
  const layers = [
    {
      num: '01',
      title: 'Per-Piece DFA',
      subtitle: 'Deterministic Finite Automata',
      icon: Cpu,
      desc: 'Each piece (Rook, Bishop, Knight, Pawn, King, Queen) has an independent DFA that validates single-ply geometry, step boundaries, and obstacle blocking without consulting move history.',
      tags: ['Regular Language', 'Ray Tracing', 'Grid Bounds'],
      badgeColor: 'border-blue-500/30 text-blue-400 bg-blue-500/10',
    },
    {
      num: '02',
      title: 'History-Dependent FSM',
      subtitle: 'Context & Memory State Machine',
      icon: History,
      desc: 'Solves the memoryless limitation of plain DFAs: tracks king/rook movement history to enforce castling rights and records the immediately preceding halfmove to govern en passant.',
      tags: ['State Vectors', 'Castling Rights', 'En Passant Memory'],
      badgeColor: 'border-amber-500/30 text-amber-400 bg-amber-500/10',
    },
    {
      num: '03',
      title: 'Game Sequence Validator',
      subtitle: 'Turn Alternation & SAN Transducer',
      icon: GitBranch,
      desc: 'Processes the full game as an ordered sequence of move tokens. Enforces strict White-Black turn alternation, disambiguates algebraic notation, and sequences board updates.',
      tags: ['Sequence Processing', 'SAN Disambiguation', 'Turn Invariant'],
      badgeColor: 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10',
    },
    {
      num: '04',
      title: 'King Safety Filter',
      subtitle: 'Virtual Lookahead Oracle',
      icon: ShieldCheck,
      desc: 'Simulates candidate moves on an ephemeral virtual board to verify the moving player does not leave their own king in check, while detecting checks delivered to the opponent.',
      tags: ['State Simulation', 'Check Invariance', 'Self-Check Prevention'],
      badgeColor: 'border-purple-500/30 text-purple-400 bg-purple-500/10',
    },
  ];

  const techStack = [
    { name: 'FastAPI', role: 'Python High-Performance ASGI Engine', icon: '⚡' },
    { name: 'Pure Python Core', role: 'Zero External Chess Engine Dependencies', icon: '🐍' },
    { name: 'React 18 & TypeScript', role: 'Type-Safe Reactive Frontend Architecture', icon: '⚛️' },
    { name: 'Tailwind CSS', role: 'Premium Dark Navy & Warm Gold Interface', icon: '🎨' },
    { name: 'Lichess Database', role: 'Real Open-Source Grandmaster Game Verification', icon: '♟️' },
    { name: 'Automata Theory', role: 'Formal Verification Hierarchy (DFA / FSM)', icon: '📐' },
  ];

  return (
    <div className="space-y-24 py-8">
      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center pt-8 sm:pt-16">
        <div className="absolute inset-0 -z-10 flex items-center justify-center pointer-events-none">
          <div className="w-[500px] h-[500px] bg-amber-500/10 rounded-full blur-[140px] opacity-60" />
          <div className="w-[400px] h-[400px] bg-blue-600/10 rounded-full blur-[120px] opacity-40 ml-48" />
        </div>

        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs text-amber-400 mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5" />
          <span className="font-semibold tracking-wide uppercase">Theory of Computation Capstone</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-300">Four-Layer Automata Engine</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-[1.15]">
          Rule-Based Chess Move <br />
          <span className="bg-gradient-to-r from-amber-400 via-amber-300 to-yellow-500 bg-clip-text text-transparent">
            Legality Validator
          </span>
        </h1>

        <p className="mt-6 text-base sm:text-lg text-slate-400 max-w-3xl mx-auto leading-relaxed">
          Not an AI chess engine or minimax bot. A formal computational system proving how
          <span className="text-amber-400 font-medium"> Deterministic Finite Automata (DFAs)</span>,
          <span className="text-amber-400 font-medium"> History-Dependent FSMs</span>, and
          <span className="text-amber-400 font-medium"> Lookahead Safety Filters</span> collaborate to validate standard chess rules.
        </p>

        {/* Hero Actions */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <button
            onClick={onStartValidating}
            className="flex items-center space-x-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-sm shadow-lg shadow-amber-500/20 hover:scale-[1.02] transition-all duration-200"
          >
            <span>Start Validating Moves</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={onExploreAutomata}
            className="flex items-center space-x-2 px-6 py-3.5 rounded-xl bg-slate-800/90 hover:bg-slate-800 text-white font-semibold text-sm border border-slate-700 hover:border-slate-600 transition-all duration-200"
          >
            <Cpu className="w-4 h-4 text-amber-400" />
            <span>Explore Automata Theory</span>
          </button>
          <button
            onClick={onOpenDataset}
            className="flex items-center space-x-2 px-6 py-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-850 text-slate-300 hover:text-white font-medium text-sm border border-slate-800 hover:border-slate-700 transition-all duration-200"
          >
            <Database className="w-4 h-4 text-slate-400" />
            <span>Test Lichess Dataset</span>
          </button>
        </div>

        {/* Quick Highlights Banner */}
        <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
          <div className="bg-[#111a2e]/80 border border-slate-800/80 p-4 rounded-xl">
            <div className="text-amber-400 font-bold text-2xl">4 Layers</div>
            <div className="text-xs text-slate-400 mt-1">Hierarchical Automata Verification</div>
          </div>
          <div className="bg-[#111a2e]/80 border border-slate-800/80 p-4 rounded-xl">
            <div className="text-amber-400 font-bold text-2xl">100 / 100</div>
            <div className="text-xs text-slate-400 mt-1">Passing Pytest Test Assertions</div>
          </div>
          <div className="bg-[#111a2e]/80 border border-slate-800/80 p-4 rounded-xl">
            <div className="text-amber-400 font-bold text-2xl">0 Engine Bias</div>
            <div className="text-xs text-slate-400 mt-1">Pure Rule Logic, Zero Heuristics</div>
          </div>
          <div className="bg-[#111a2e]/80 border border-slate-800/80 p-4 rounded-xl">
            <div className="text-amber-400 font-bold text-2xl">Full PGN</div>
            <div className="text-xs text-slate-400 mt-1">Lichess Database Validation</div>
          </div>
        </div>
      </section>

      {/* The Four Layers Architecture Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <div className="text-xs font-bold uppercase tracking-wider text-amber-400 mb-2">
            Automata Theory Breakdown
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            The Four Validation Layers
          </h2>
          <p className="text-sm text-slate-400 mt-3">
            Every candidate move submitted by a user or game transcript must pass sequentially through all four automata stages.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
          {layers.map((layer) => {
            const Icon = layer.icon;
            return (
              <div
                key={layer.num}
                className="group relative bg-[#111a2e]/70 hover:bg-[#152238] border border-slate-800 hover:border-amber-500/40 rounded-2xl p-6 sm:p-8 transition-all duration-300 shadow-lg hover:shadow-amber-500/5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      Layer {layer.num}
                    </span>
                    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${layer.badgeColor}`}>
                      {layer.subtitle}
                    </span>
                  </div>

                  <div className="flex items-start space-x-4 mb-4">
                    <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60 text-amber-400 group-hover:scale-105 transition-transform">
                      <Icon className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white group-hover:text-amber-400 transition-colors">
                        {layer.title}
                      </h3>
                      <p className="text-xs text-slate-400 mt-1">{layer.subtitle}</p>
                    </div>
                  </div>

                  <p className="text-sm text-slate-300 leading-relaxed">
                    {layer.desc}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-wrap gap-2">
                  {layer.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900/90 text-slate-400 border border-slate-800"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Academic Importance: Theory of Computation vs Chess Engine */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-br from-[#111a2e] via-[#0d162a] to-[#142036] border border-amber-500/20 rounded-3xl p-8 sm:p-12 relative overflow-hidden shadow-2xl">
          <div className="max-w-3xl space-y-6">
            <div className="inline-flex items-center space-x-2 text-xs font-bold text-amber-400 uppercase tracking-wider">
              <Layers className="w-4 h-4" />
              <span>Core Academic Problem Statement</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              Why Model Chess Rules as Automata Instead of a Stockfish Bot?
            </h2>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Standard chess engines focus on position evaluation ($+1.5$, $-0.8$), alpha-beta search trees, and neural network value functions.
              In contrast, <strong>ChessMove Validator</strong> is an exercise in <em>Chomsky hierarchy language recognition</em>.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="bg-[#0b1120]/80 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 mb-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>What This Project Is</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  A mathematical decision procedure proving which chess rules require finite memory (Layer 1 DFA), which require bounded state vectors (Layer 2 FSM), and which require lookahead verification (Layer 4).
                </p>
              </div>
              <div className="bg-[#0b1120]/80 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center space-x-2 text-xs font-bold text-red-400 mb-1">
                  <Lock className="w-4 h-4 text-red-400" />
                  <span>What This Project Is Not</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Not a computer opponent, minimax tree evaluator, or evaluation engine. It never suggests best moves; it strictly decides whether a move belongs to the regular/context-sensitive language of legal chess moves.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Production Engineering Architecture
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-2">
            Built for seamless multi-platform deployment on Vercel and Render.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {techStack.map((tech) => (
            <div
              key={tech.name}
              className="bg-[#111a2e]/60 border border-slate-800 rounded-xl p-5 flex items-center space-x-4 hover:border-slate-700 transition-colors"
            >
              <div className="text-2xl p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                {tech.icon}
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{tech.name}</h4>
                <p className="text-xs text-slate-400 mt-0.5">{tech.role}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Footer Card */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 text-center">
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-t from-slate-900 to-[#10172a] border border-slate-800 shadow-xl space-y-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-white">
            Ready to explore interactive automata chess validation?
          </h2>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            Test custom moves, drag pieces on the interactive board, watch real-time layer decisions, or validate entire PGN game databases.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <button
              onClick={onStartValidating}
              className="px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm shadow-md shadow-amber-500/20 transition-all"
            >
              Open Interactive Validator
            </button>
            <button
              onClick={onExploreAutomata}
              className="px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium text-sm border border-slate-700 transition-all"
            >
              View Automata State Diagrams
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
