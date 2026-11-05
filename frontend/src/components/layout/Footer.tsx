import React from 'react';
import { Shield, BookOpen, ExternalLink, Code2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-[#070b14] border-t border-slate-900 text-slate-400 py-12 px-4 sm:px-6 lg:px-8 mt-20">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="space-y-4 md:col-span-2">
          <div className="flex items-center space-x-2">
            <span className="text-xl">♞</span>
            <span className="text-base font-bold text-white tracking-tight">ChessMove Validator</span>
            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Automata Theory Project
            </span>
          </div>
          <p className="text-sm text-slate-400 max-w-md leading-relaxed">
            A specialized academic rule-based chess legality engine demonstrating the power of formal language hierarchy:
            Deterministic Finite Automata (Layer 1), History-Dependent FSMs (Layer 2), Turn Sequencing Transducers (Layer 3),
            and Lookahead Safety Filters (Layer 4).
          </p>
          <div className="flex items-center space-x-4 text-xs text-slate-500">
            <span>Pure Automata Rules</span>
            <span>•</span>
            <span>Zero External Chess Engines</span>
            <span>•</span>
            <span>FastAPI + React TypeScript</span>
          </div>
        </div>

        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-4 flex items-center space-x-2">
            <Shield className="w-3.5 h-3.5 text-amber-400" />
            <span>The Four Layers</span>
          </h4>
          <ul className="space-y-2 text-xs">
            <li><span className="text-amber-400/90 font-medium">Layer 1:</span> Piece-specific DFAs</li>
            <li><span className="text-amber-400/90 font-medium">Layer 2:</span> Castling & En Passant FSMs</li>
            <li><span className="text-amber-400/90 font-medium">Layer 3:</span> Game Sequence Validator</li>
            <li><span className="text-amber-400/90 font-medium">Layer 4:</span> Safety & Check Filter</li>
          </ul>
        </div>

        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-4 flex items-center space-x-2">
            <BookOpen className="w-3.5 h-3.5 text-amber-400" />
            <span>Academic Attribution</span>
          </h4>
          <ul className="space-y-2 text-xs">
            <li>
              <a
                href="https://database.lichess.org/"
                target="_blank"
                rel="noreferrer"
                className="hover:text-amber-400 transition-colors flex items-center space-x-1"
              >
                <span>Lichess Open Database (CC0)</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </li>
            <li>Theory of Computation / TOC College Capstone</li>
            <li className="pt-2 text-slate-500">
              Designed & Engineered with pure rule-based automata verification.
            </li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto mt-8 pt-8 border-t border-slate-900/80 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
        <p>© 2026 ChessMove Validator. College Theory of Computation Project.</p>
        <p className="mt-2 sm:mt-0 flex items-center space-x-1">
          <Code2 className="w-3.5 h-3.5 text-amber-400" />
          <span>Automata Theory in Practical Software Engineering</span>
        </p>
      </div>
    </footer>
  );
};
