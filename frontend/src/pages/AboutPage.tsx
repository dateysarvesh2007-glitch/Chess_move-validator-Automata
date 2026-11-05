import React from 'react';
import { 
  BookOpen, 
  Layers, 
  ExternalLink, 
  ShieldAlert, 
  Cpu,
  GraduationCap
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6">
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
          <GraduationCap className="w-4 h-4" />
          <span>Academic Capstone Thesis & Documentation</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          ChessMove Validator: Theoretical Foundation & Architecture
        </h1>
        <p className="text-sm text-slate-400 mt-2 leading-relaxed">
          Coursework & Project Defense Documentation for Formal Languages and Automata Theory (Theory of Computation).
        </p>
      </div>

      {/* 1. Problem Statement & Objectives */}
      <section className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4 shadow-xl">
        <h2 className="text-xl font-bold text-white flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-amber-400" />
          <span>1. Problem Statement & Academic Objectives</span>
        </h2>
        <div className="text-sm text-slate-300 space-y-3 leading-relaxed">
          <p>
            Standard software engineering implementations of chess legality rely heavily on external C/C++ engine libraries
            (such as Stockfish or python-chess) or monolithic brute-force state trees. While functionally effective, these
            approaches obscure the <em>automata-theoretic classification</em> of chess rules.
          </p>
          <p>
            <strong>The Objective:</strong> To construct a pure, rule-based chess move legality verifier from first principles,
            deconstructing complex chess rules into formal automata tiers:
          </p>
          <ul className="list-disc list-inside text-xs text-slate-400 space-y-1 pl-2">
            <li>Identify which subset of chess rules forms a strictly regular language recognized by Deterministic Finite Automata (DFA).</li>
            <li>Demonstrate why memoryless DFAs fail for castling and en passant, requiring history-dependent state vectors.</li>
            <li>Formalize game sequence processing as a deterministic transducer with strict turn alternation.</li>
            <li>Model king safety and check prevention as an invariant filter over virtual state simulations.</li>
          </ul>
        </div>
      </section>

      {/* 2. Automata Theory Connection (Chomsky Hierarchy) */}
      <section className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4 shadow-xl">
        <h2 className="text-xl font-bold text-white flex items-center space-x-2">
          <Cpu className="w-5 h-5 text-amber-400" />
          <span>2. Chomsky Hierarchy & Formal Classification</span>
        </h2>
        <div className="overflow-x-auto rounded-xl border border-slate-800 mt-4">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3">Automata Layer</th>
                <th className="p-3">Formal Grammar / Automaton</th>
                <th className="p-3">Computational Power</th>
                <th className="p-3">Why Required</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-950/40 text-slate-300">
              <tr>
                <td className="p-3 font-bold text-white">Layer 1: Piece DFA</td>
                <td className="p-3">Type 3: Regular Grammar (DFA)</td>
                <td className="p-3 text-amber-400">Finite State Machine</td>
                <td className="p-3 text-slate-400">Fixed 8x8 grid geometry and finite ray paths.</td>
              </tr>
              <tr>
                <td className="p-3 font-bold text-white">Layer 2: History FSM</td>
                <td className="p-3">Mealy/Moore Machine with Vector Tape</td>
                <td className="p-3 text-amber-400">Extended Finite State Transducer</td>
                <td className="p-3 text-slate-400">Non-local temporal conditions (castling rights, en passant).</td>
              </tr>
              <tr>
                <td className="p-3 font-bold text-white">Layer 3: Sequence FSM</td>
                <td className="p-3">Regular Language: (White · Black)*</td>
                <td className="p-3 text-amber-400">Sequential State Processor</td>
                <td className="p-3 text-slate-400">Strict turn order and algebraic notation parsing.</td>
              </tr>
              <tr>
                <td className="p-3 font-bold text-white">Layer 4: Safety Filter</td>
                <td className="p-3">Non-Terminal Invariant Oracle</td>
                <td className="p-3 text-amber-400">Lookahead State Projection</td>
                <td className="p-3 text-slate-400">Pins and self-check prevention across candidate plies.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 3. System Architecture */}
      <section className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4 shadow-xl">
        <h2 className="text-xl font-bold text-white flex items-center space-x-2">
          <Layers className="w-5 h-5 text-amber-400" />
          <span>3. System Architecture & Component Interaction</span>
        </h2>
        <p className="text-sm text-slate-300 leading-relaxed">
          The application follows a decoupled full-stack architecture. The React TypeScript frontend serves strictly as an
          interactive terminal and state visualizer. <strong>The frontend never computes move legality</strong>; every drag-and-drop
          or click event sends a REST POST request to the Python backend running FastAPI, which coordinates the four validation layers.
        </p>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 space-y-2">
          <div className="text-amber-400 font-bold">Data Flow:</div>
          <div>User Interaction (React UI) → REST API POST /api/game/move</div>
          <div className="pl-4">↳ Layer 3 validates turn order & coordinates</div>
          <div className="pl-4">↳ Layer 1 validates piece DFA geometry & obstacle clear line</div>
          <div className="pl-4">↳ Layer 2 verifies castling rights or en passant eligibility</div>
          <div className="pl-4">↳ Layer 4 simulates move on virtual cloned board and checks King safety</div>
          <div>JSON Response with ACCEPT/REJECT, reason, FEN, board dict, and layer analysis</div>
        </div>
      </section>

      {/* 4. Dataset Source & Licensing */}
      <section className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4 shadow-xl">
        <h2 className="text-xl font-bold text-white flex items-center space-x-2">
          <ExternalLink className="w-5 h-5 text-amber-400" />
          <span>4. Dataset Source & Attribution</span>
        </h2>
        <div className="text-sm text-slate-300 space-y-3 leading-relaxed">
          <p>
            Real chess game testing is powered by standard PGN sequences sourced from the{' '}
            <a
              href="https://database.lichess.org/"
              target="_blank"
              rel="noreferrer"
              className="text-amber-400 hover:underline font-semibold"
            >
              Lichess Open Database
            </a>
            , released under the Creative Commons CC0 Public Domain dedication.
          </p>
          <p className="text-xs text-slate-400">
            A curated sample set of approximately 500–1,000 games is maintained on the server alongside custom negative test suites
            (games with deliberately illegal moves such as moving pinned pieces or jumping obstructed paths) to demonstrate
            rigorous positive and negative verification.
          </p>
        </div>
      </section>

      {/* 5. Limitations & Future Scope */}
      <section className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4 shadow-xl">
        <h2 className="text-xl font-bold text-white flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-amber-400" />
          <span>5. Limitations & Future Scope</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <h4 className="font-bold text-amber-400">Known Deliberate Limitations</h4>
            <ul className="list-disc list-inside text-slate-400 space-y-1">
              <li>No AI evaluation or minimax search tree (by academic design).</li>
              <li>No opening book suggestions or engine eval numbers (+1.2).</li>
              <li>Focus is strictly on boolean legality and educational automata proofs.</li>
            </ul>
          </div>
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <h4 className="font-bold text-emerald-400">Future Scope</h4>
            <ul className="list-disc list-inside text-slate-400 space-y-1">
              <li>Visual step-by-step DFA animation highlighting active node transitions per ply.</li>
              <li>Exporting formal LaTeX / DOT state graph diagrams for academic publications.</li>
              <li>Support for chess variants (e.g. Fischer Random / Chess960 castling rules).</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
};
