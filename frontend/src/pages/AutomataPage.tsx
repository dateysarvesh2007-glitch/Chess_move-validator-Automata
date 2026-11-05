import React, { useState } from 'react';
import { 
  Cpu, 
  History, 
  GitBranch, 
  ShieldCheck, 
  Layers, 
  HelpCircle, 
  CheckCircle2, 
  BookOpen, 
  Sparkles, 
  Zap, 
  Code 
} from 'lucide-react';

export const AutomataPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'layer1' | 'layer2' | 'layer3' | 'layer4' | 'flow' | 'viva'>('layer1');
  const [selectedPiece, setSelectedPiece] = useState<'knight' | 'bishop' | 'rook' | 'pawn' | 'queen' | 'king'>('knight');

  const pieceData: Record<string, {
    name: string;
    symbol: string;
    tuple: {
      states: string[];
      alphabet: string[];
      start: string;
      accept: string[];
      reject: string[];
    };
    transitions: Array<{ from: string; input: string; to: string; type: 'accept' | 'reject' | 'step' }>;
    rayScan: boolean;
    explanation: string;
    vivaInsight: string;
  }> = {
    knight: {
      name: 'Knight DFA',
      symbol: '♞',
      tuple: {
        states: ['q₀ (START)', 'q₁ (L_SHAPE_VERIFIED)', 'q_acc (ACCEPT)', 'q_rej (REJECT)'],
        alphabet: ['Δx² + Δy² == 5', 'dest_empty_or_enemy', 'dest_friendly', 'other_vector'],
        start: 'q₀',
        accept: ['q_acc'],
        reject: ['q_rej'],
      },
      transitions: [
        { from: 'q₀', input: '(|Δrow|,|Δcol|) in {(1,2),(2,1)}', to: 'q₁', type: 'step' },
        { from: 'q₀', input: 'any other (Δrow, Δcol)', to: 'q_rej (INVALID_GEOMETRY)', type: 'reject' },
        { from: 'q₁', input: 'destination is Empty OR Enemy', to: 'q_acc (ACCEPT)', type: 'accept' },
        { from: 'q₁', input: 'destination is Friendly Piece', to: 'q_rej (BLOCKED_BY_FRIENDLY)', type: 'reject' },
      ],
      rayScan: false,
      explanation: 'Knights are the only pieces that leap over intervening squares. Hence, the Knight DFA does not require an intermediate ray-casting loop or obstacle scanning. It only evaluates destination occupancy.',
      vivaInsight: 'Because ray scanning is omitted, the Knight DFA requires the fewest internal states of any piece in Layer 1.',
    },
    bishop: {
      name: 'Bishop DFA',
      symbol: '♝',
      tuple: {
        states: ['q₀ (START)', 'q₁ (DIAGONAL_VERIFIED)', 'q_scan (RAY_CAST_LOOP)', 'q_acc (ACCEPT)', 'q_rej (REJECT)'],
        alphabet: ['|Δrow| == |Δcol| > 0', 'sq_between_empty', 'sq_between_occupied', 'dest_empty_or_enemy', 'dest_friendly'],
        start: 'q₀',
        accept: ['q_acc'],
        reject: ['q_rej'],
      },
      transitions: [
        { from: 'q₀', input: '|Δrow| == |Δcol| > 0', to: 'q₁', type: 'step' },
        { from: 'q₀', input: '|Δrow| != |Δcol|', to: 'q_rej (NON_DIAGONAL_MOVE)', type: 'reject' },
        { from: 'q₁', input: 'step along ray: intervening square empty', to: 'q_scan', type: 'step' },
        { from: 'q_scan', input: 'intervening square occupied by piece', to: 'q_rej (PATH_OBSTRUCTED)', type: 'reject' },
        { from: 'q_scan', input: 'destination reached AND (dest empty or enemy)', to: 'q_acc (ACCEPT)', type: 'accept' },
        { from: 'q_scan', input: 'destination reached AND dest friendly', to: 'q_rej (FRIENDLY_OCCUPIED)', type: 'reject' },
      ],
      rayScan: true,
      explanation: 'Bishops travel exclusively along diagonals (slope = ±1). The DFA enforces strict ray tracing: every single intermediate coordinate between origin and destination must be strictly empty.',
      vivaInsight: 'Bishop moves preserve square color parity: (row + col) mod 2 is invariant across all valid transitions.',
    },
    rook: {
      name: 'Rook DFA',
      symbol: '♜',
      tuple: {
        states: ['q₀ (START)', 'q₁ (ORTHOGONAL_VERIFIED)', 'q_scan (RAY_SCAN)', 'q_acc (ACCEPT)', 'q_rej (REJECT)'],
        alphabet: ['Δrow == 0 or Δcol == 0', 'intervening_empty', 'intervening_blocked', 'dest_target_valid'],
        start: 'q₀',
        accept: ['q_acc'],
        reject: ['q_rej'],
      },
      transitions: [
        { from: 'q₀', input: '(Δrow == 0 and Δcol != 0) OR (Δcol == 0 and Δrow != 0)', to: 'q₁', type: 'step' },
        { from: 'q₀', input: 'Δrow != 0 and Δcol != 0', to: 'q_rej (NON_ORTHOGONAL)', type: 'reject' },
        { from: 'q₁', input: 'step along rank or file: square empty', to: 'q_scan', type: 'step' },
        { from: 'q_scan', input: 'intervening piece detected on file/rank', to: 'q_rej (BLOCKED_PATH)', type: 'reject' },
        { from: 'q_scan', input: 'destination reached, not occupied by friendly', to: 'q_acc (ACCEPT)', type: 'accept' },
        { from: 'q_scan', input: 'destination reached, occupied by friendly', to: 'q_rej (FRIENDLY_OCCUPIED)', type: 'reject' },
      ],
      rayScan: true,
      explanation: 'Rooks move horizontally across ranks or vertically along files. An 8x8 bounded grid limits ray length to at most 7 squares, guaranteeing deterministic finite termination.',
      vivaInsight: 'Standard rook movements in Layer 1 do not include castling. Castling requires Layer 2 history validation.',
    },
    queen: {
      name: 'Queen DFA',
      symbol: '♛',
      tuple: {
        states: ['q₀ (START)', 'q_rook (ROOK_DELEGATE)', 'q_bishop (BISHOP_DELEGATE)', 'q_acc (ACCEPT)', 'q_rej (REJECT)'],
        alphabet: ['Orthogonal Vector', 'Diagonal Vector', 'Line-of-Sight Rays', 'Target Squares'],
        start: 'q₀',
        accept: ['q_acc'],
        reject: ['q_rej'],
      },
      transitions: [
        { from: 'q₀', input: 'horizontal or vertical vector', to: 'q_rook', type: 'step' },
        { from: 'q₀', input: 'diagonal vector (|Δrow| == |Δcol|)', to: 'q_bishop', type: 'step' },
        { from: 'q₀', input: 'neither orthogonal nor diagonal', to: 'q_rej (INVALID_QUEEN_VECTOR)', type: 'reject' },
        { from: 'q_rook', input: 'Rook DFA yields ACCEPT', to: 'q_acc (ACCEPT)', type: 'accept' },
        { from: 'q_bishop', input: 'Bishop DFA yields ACCEPT', to: 'q_acc (ACCEPT)', type: 'accept' },
      ],
      rayScan: true,
      explanation: 'The Queen DFA is mathematically modeled as the formal language union: L(Queen) = L(Rook) ∪ L(Bishop). By closure properties of regular languages, the union of two DFAs is also recognized by a DFA.',
      vivaInsight: 'Closure Property Proof: Regular languages are closed under union; thus, combining Rook and Bishop behaviors preserves regular language status.',
    },
    pawn: {
      name: 'Pawn DFA',
      symbol: '♟',
      tuple: {
        states: ['q₀ (START)', 'q_one (ONE_STEP)', 'q_two (TWO_STEP)', 'q_diag (CAPTURE_DIAG)', 'q_promo (PROMOTION)', 'q_acc', 'q_rej'],
        alphabet: ['Direction forward', 'Initial rank (2 or 7)', 'Target square empty/enemy', 'Last rank (8 or 1)'],
        start: 'q₀',
        accept: ['q_acc'],
        reject: ['q_rej'],
      },
      transitions: [
        { from: 'q₀', input: '1 square forward AND destination is empty', to: 'q_one', type: 'step' },
        { from: 'q₀', input: '2 squares forward from starting rank AND path clear', to: 'q_two', type: 'step' },
        { from: 'q₀', input: '1 square diagonal AND destination contains enemy', to: 'q_diag', type: 'step' },
        { from: 'q_one', input: 'target rank is 8 (White) or 1 (Black)', to: 'q_promo', type: 'step' },
        { from: 'q_one', input: 'target rank is intermediate (3 to 7)', to: 'q_acc (ACCEPT)', type: 'accept' },
        { from: 'q_two', input: 'destination square empty', to: 'q_acc (ACCEPT)', type: 'accept' },
        { from: 'q_diag', input: 'target rank is 8 or 1', to: 'q_promo', type: 'step' },
        { from: 'q_promo', input: 'valid promotion piece selected (Q, R, B, N)', to: 'q_acc (ACCEPT)', type: 'accept' },
      ],
      rayScan: false,
      explanation: 'Pawns are unique: their forward alphabet requires empty squares, while their diagonal alphabet requires enemy pieces. Two-step advances are valid strictly from the pawn initial rank.',
      vivaInsight: 'En passant is intentionally omitted from the Pawn DFA because it requires memory of the opponent prior move (Layer 2).',
    },
    king: {
      name: 'King DFA (Non-Castling)',
      symbol: '♚',
      tuple: {
        states: ['q₀ (START)', 'q_step (ONE_SQUARE_RANGE)', 'q_acc (ACCEPT)', 'q_rej (REJECT)'],
        alphabet: ['max(|Δrow|, |Δcol|) == 1', 'dest_empty_or_enemy', 'dest_friendly'],
        start: 'q₀',
        accept: ['q_acc'],
        reject: ['q_rej'],
      },
      transitions: [
        { from: 'q₀', input: 'max(|Δrow|, |Δcol|) == 1', to: 'q_step', type: 'step' },
        { from: 'q₀', input: 'max(|Δrow|, |Δcol|) > 1 (excluding castling)', to: 'q_rej (STRIDE_TOO_LARGE)', type: 'reject' },
        { from: 'q_step', input: 'destination empty OR enemy piece', to: 'q_acc (ACCEPT)', type: 'accept' },
        { from: 'q_step', input: 'destination friendly piece', to: 'q_rej (FRIENDLY_OCCUPIED)', type: 'reject' },
      ],
      rayScan: false,
      explanation: 'The King DFA in Layer 1 only checks local 1-square adjacency. Whether the target square is attacked is deferred to Layer 4 (Check Safety Filter), and castling is deferred to Layer 2 (History FSM).',
      vivaInsight: 'Decoupling king geometry (Layer 1) from king safety (Layer 4) prevents infinite recursion in check detection.',
    },
  };

  const vivaQuestions = [
    {
      q: 'Why cannot chess move legality be validated with a single DFA alone?',
      a: 'A Deterministic Finite Automaton (DFA) has zero external memory; its state transitions can only depend on the current symbol and state. Chess rules like castling (requires knowing if the King or Rook ever moved in past plies) and en passant (requires knowing if the opponent previous move was a two-square pawn push) make legality history-dependent. Therefore, a memoryless DFA is insufficient, requiring an extended FSM (Layer 2) with historical state vectors.',
    },
    {
      q: 'What is the computational complexity of the Check-Safety Filter (Layer 4)?',
      a: 'For an 8x8 board, Layer 4 runs in O(1) constant time because the board size is bounded (64 squares, at most 32 pieces). To verify king safety, the engine projects inverse rays along 8 directions (for Queen, Rook, Bishop), checks 8 knight jump coordinates, and inspects pawn attacks. This bounded search requires at most 64 operations.',
    },
    {
      q: 'How does Layer 3 enforce the language grammar of a chess game?',
      a: 'Layer 3 acts as a sequential transducer enforcing the regular expression L = (White_Move · Black_Move)*. If an input attempts two consecutive white moves (e.g. w1, w2) or black moves out of turn, Layer 3 immediately halts in a non-accepting trap state.',
    },
    {
      q: 'Why is the Queen DFA described as a union of two regular languages?',
      a: 'Under formal language theory, if L₁ = L(Rook) and L₂ = L(Bishop) are both regular languages recognized by DFAs M₁ and M₂, then L(Queen) = L₁ ∪ L₂ is also regular because regular languages are closed under union. The Queen DFA branches to Rook or Bishop transition logic depending on the initial displacement vector.',
    },
    {
      q: 'How does your engine prevent infinite recursive loops during check detection?',
      a: 'When King A checks if square s is attacked, it queries enemy pieces (Layer 1 movements). Those enemy piece queries do NOT recursively invoke Layer 4 safety checks on themselves—they only evaluate raw attacking geometry and obstacle blocking. This strict layering prevents cyclic recursive deadlocks.',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6">
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
          <BookOpen className="w-4 h-4" />
          <span>Academic Thesis & Theory of Computation Guide</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Automata Theory & Formal Language Architecture
        </h1>
        <p className="text-sm text-slate-400 mt-2 max-w-3xl leading-relaxed">
          Comprehensive visual explanations and mathematical state transition tables for college viva examinations, project presentations, and research papers.
        </p>

        {/* Tab Switcher */}
        <div className="mt-8 flex flex-wrap gap-2 border-b border-slate-800 pb-2">
          {[
            { id: 'layer1', label: 'Layer 1: Piece DFAs', icon: Cpu },
            { id: 'layer2', label: 'Layer 2: History FSM', icon: History },
            { id: 'layer3', label: 'Layer 3: Game Sequencer', icon: GitBranch },
            { id: 'layer4', label: 'Layer 4: Safety & Check', icon: ShieldCheck },
            { id: 'flow', label: 'Full Layer Flowchart', icon: Layers },
            { id: 'viva', label: 'College Viva Q&A', icon: HelpCircle },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
                    : 'bg-[#111a2e] text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab 1: Layer 1 Piece DFAs */}
      {activeTab === 'layer1' && (
        <div className="space-y-8 animate-fadeIn">
          {/* Piece Selector */}
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 mr-2">Select Piece:</span>
            {Object.keys(pieceData).map((pKey) => {
              const p = pieceData[pKey];
              const isSel = selectedPiece === pKey;
              return (
                <button
                  key={pKey}
                  onClick={() => setSelectedPiece(pKey as any)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    isSel
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm'
                      : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  <span className="text-base">{p.symbol}</span>
                  <span className="capitalize">{pKey}</span>
                </button>
              );
            })}
          </div>

          {/* Piece DFA Spec Card */}
          <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800/80 pb-6">
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-3xl text-amber-400">
                  {pieceData[selectedPiece].symbol}
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">
                    {pieceData[selectedPiece].name}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Deterministic Finite Automaton: M = (Q, Σ, δ, q₀, F)
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3 text-xs">
                <span className={`px-3 py-1 rounded-full font-semibold border ${
                  pieceData[selectedPiece].rayScan
                    ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                    : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                }`}>
                  {pieceData[selectedPiece].rayScan ? 'Requires Line-of-Sight Ray Scan' : 'Direct Target Leap (No Ray Obstacles)'}
                </span>
              </div>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed">
              {pieceData[selectedPiece].explanation}
            </p>

            {/* Formal 5-Tuple Box */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-900/80 border border-slate-800/80 rounded-xl p-5 text-xs font-mono">
              <div>
                <span className="text-amber-400 font-bold block mb-1">States (Q):</span>
                <span className="text-slate-300">{pieceData[selectedPiece].tuple.states.join(', ')}</span>
              </div>
              <div>
                <span className="text-amber-400 font-bold block mb-1">Alphabet (Σ):</span>
                <span className="text-slate-300">{pieceData[selectedPiece].tuple.alphabet.join(' | ')}</span>
              </div>
              <div>
                <span className="text-amber-400 font-bold block mb-1">Start State (q₀):</span>
                <span className="text-slate-300">{pieceData[selectedPiece].tuple.start}</span>
              </div>
              <div>
                <span className="text-amber-400 font-bold block mb-1">Accept States (F):</span>
                <span className="text-emerald-400 font-bold">{pieceData[selectedPiece].tuple.accept.join(', ')}</span>
              </div>
            </div>

            {/* Transition Table */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center space-x-2">
                <Code className="w-3.5 h-3.5 text-amber-400" />
                <span>State Transition Table (δ: Q × Σ → Q)</span>
              </h4>

              <div className="overflow-x-auto rounded-xl border border-slate-800">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="p-3">Current State</th>
                      <th className="p-3">Input Condition (Board Predicate)</th>
                      <th className="p-3">Next State</th>
                      <th className="p-3">Verdict</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                    {pieceData[selectedPiece].transitions.map((t, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="p-3 font-semibold text-slate-200">{t.from}</td>
                        <td className="p-3 text-slate-300">{t.input}</td>
                        <td className="p-3 font-bold text-amber-400">{t.to}</td>
                        <td className="p-3">
                          {t.type === 'accept' && (
                            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">ACCEPT</span>
                          )}
                          {t.type === 'reject' && (
                            <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-300 font-bold">REJECT</span>
                          )}
                          {t.type === 'step' && (
                            <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold">TRANSITION</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Viva Insight Box */}
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start space-x-3 text-xs">
              <Sparkles className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-amber-300">Viva Insight: </span>
                <span className="text-slate-300">{pieceData[selectedPiece].vivaInsight}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Layer 2 History FSM */}
      {activeTab === 'layer2' && (
        <div className="space-y-8 animate-fadeIn">
          <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
            <div className="border-b border-slate-800 pb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">Layer 2: Memory & Context</span>
              <h3 className="text-2xl font-bold text-white mt-1">History-Dependent Finite State Machine</h3>
              <p className="text-xs text-slate-400 mt-1">
                Extends classical DFA with state vectors to govern temporal chess invariants (Castling and En Passant).
              </p>
            </div>

            {/* Subsystem 1: Castling FSM */}
            <div className="space-y-4">
              <h4 className="text-base font-bold text-amber-400 flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>1. Castling Rights State Machine</span>
              </h4>
              <p className="text-sm text-slate-300 leading-relaxed">
                Castling is an irreversible transition. Once the King moves, both castling rights are revoked permanently ($S \to \emptyset$).
                If a Rook moves, only that specific flank right is revoked.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-amber-400 font-bold">State: KQkq</div>
                  <p className="text-slate-400 mt-1">Initial state: Both sides retain kingside and queenside castling rights.</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-amber-400 font-bold">Transition: King Move</div>
                  <p className="text-slate-400 mt-1">King moves 1 square: instantly transitions to state where all castling rights for that color are false.</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-amber-400 font-bold">Check Filter Cross-Check</div>
                  <p className="text-slate-400 mt-1">Intermediate transit squares (f1/g1 or c1/d1) must not be attacked by opponent pieces.</p>
                </div>
              </div>
            </div>

            {/* Subsystem 2: En Passant FSM */}
            <div className="space-y-4 pt-6 border-t border-slate-800/80">
              <h4 className="text-base font-bold text-amber-400 flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>2. En Passant Transient State Machine</span>
              </h4>
              <p className="text-sm text-slate-300 leading-relaxed">
                En passant is an ephemeral, single-ply state window. If an opponent advances a pawn two squares (e.g., e7 → e5),
                an en passant target square (e6) is activated. If the player does not execute the capture on the <em>immediately following move</em>,
                the target expires and transitions back to <code className="text-amber-400">None</code>.
              </p>

              <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs space-y-2">
                <div className="flex items-center space-x-2 text-slate-300">
                  <span className="text-amber-400 font-bold">State Transition:</span>
                  <span>S(en_passant = None) --[opponent pawn 2-square push]→ S'(en_passant = target_sq)</span>
                </div>
                <div className="flex items-center space-x-2 text-slate-300">
                  <span className="text-amber-400 font-bold">Next Halfmove:</span>
                  <span>S'(target_sq) --[any move other than capturing target]→ S''(en_passant = None)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Layer 3 Sequence Validator */}
      {activeTab === 'layer3' && (
        <div className="space-y-8 animate-fadeIn">
          <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
            <div className="border-b border-slate-800 pb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">Layer 3: Sequence Grammar</span>
              <h3 className="text-2xl font-bold text-white mt-1">Game Sequence & Turn Alternator FSM</h3>
              <p className="text-xs text-slate-400 mt-1">
                Enforces the regular language L = (White · Black)* across the chronological move tape.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Turn Alternation State Machine</span>
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  The system maintains binary turn states: <code className="text-amber-400">WHITE_TO_MOVE</code> and <code className="text-amber-400">BLACK_TO_MOVE</code>.
                  Every accepted move transitions state:
                </p>
                <div className="font-mono text-xs text-slate-400 bg-slate-950 p-3 rounded-lg border border-slate-800">
                  δ(WHITE_TO_MOVE, legal_white_move) → BLACK_TO_MOVE<br />
                  δ(BLACK_TO_MOVE, legal_black_move) → WHITE_TO_MOVE<br />
                  δ(WHITE_TO_MOVE, black_move_attempt) → TRAP_REJECT
                </div>
              </div>

              <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>SAN Parsing & Disambiguation Transducer</span>
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Translates algebraic notation (e.g. <code>Nbd2</code>, <code>Rfe1</code>, <code>O-O</code>) into concrete coordinate pairs.
                  When two pieces of the same type can move to the same square, file/rank qualifiers disambiguate the transition.
                </p>
                <div className="font-mono text-xs text-slate-400 bg-slate-950 p-3 rounded-lg border border-slate-800">
                  Candidate Filter: Pieces(type, color) ∩ CanReach(dest) ∩ Matches(file/rank) == 1
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Layer 4 Safety & Check */}
      {activeTab === 'layer4' && (
        <div className="space-y-8 animate-fadeIn">
          <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
            <div className="border-b border-slate-800 pb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">Layer 4: Invariant Oracle</span>
              <h3 className="text-2xl font-bold text-white mt-1">King Safety & Check Verification Filter</h3>
              <p className="text-xs text-slate-400 mt-1">
                Lookahead state simulation that rejects candidate moves which leave or expose the player's own king to check.
              </p>
            </div>

            <div className="space-y-4">
              <h4 className="text-sm font-bold text-white">Lookahead Simulation Pipeline:</h4>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs font-mono">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
                  <div className="text-amber-400 font-bold mb-1">Step 1</div>
                  <div className="text-slate-300">Clone State (S → S')</div>
                  <div className="text-[10px] text-slate-500 mt-1">Virtual ephemeral board</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
                  <div className="text-amber-400 font-bold mb-1">Step 2</div>
                  <div className="text-slate-300">Apply Move on S'</div>
                  <div className="text-[10px] text-slate-500 mt-1">Displace piece & remove captures</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
                  <div className="text-amber-400 font-bold mb-1">Step 3</div>
                  <div className="text-slate-300">Project Opponent Rays</div>
                  <div className="text-[10px] text-slate-500 mt-1">Check if own king coordinate attacked</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
                  <div className="text-emerald-400 font-bold mb-1">Step 4</div>
                  <div className="text-slate-300">Verdict & Check (+)</div>
                  <div className="text-[10px] text-slate-500 mt-1">Accept if safe; add + if checks enemy</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Full Architecture Flowchart */}
      {activeTab === 'flow' && (
        <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-10 space-y-8 shadow-xl animate-fadeIn">
          <div className="border-b border-slate-800 pb-4 text-center max-w-xl mx-auto">
            <h3 className="text-2xl font-bold text-white">Complete Four-Layer Verification Pipeline</h3>
            <p className="text-xs text-slate-400 mt-1">
              Data flow showing how candidate moves traverse all four layers sequentially before committing to the board state.
            </p>
          </div>

          <div className="flex flex-col items-center space-y-4 max-w-2xl mx-auto font-mono text-xs">
            <div className="w-full p-4 rounded-xl bg-slate-900 border border-slate-700 text-center text-white font-bold">
              User Move Input: from_square → to_square (or SAN token)
            </div>

            <div className="text-amber-400 font-bold text-lg">↓</div>

            <div className="w-full p-4 rounded-xl bg-slate-850 border border-slate-700 space-y-1">
              <div className="text-amber-400 font-bold">Layer 3: Sequence & Turn Alternator</div>
              <p className="text-[11px] text-slate-400 font-sans">
                Is it the player's turn? Does the piece exist? Disambiguate algebraic notation if applicable.
              </p>
            </div>

            <div className="text-amber-400 font-bold text-lg">↓</div>

            <div className="w-full p-4 rounded-xl bg-slate-850 border border-slate-700 space-y-1">
              <div className="text-amber-400 font-bold">Layer 1: Per-Piece DFA</div>
              <p className="text-[11px] text-slate-400 font-sans">
                Does candidate move match piece geometric grammar? Is the path unobstructed? (Rook, Bishop, Knight, Pawn, King, Queen).
              </p>
            </div>

            <div className="text-amber-400 font-bold text-lg">↓</div>

            <div className="w-full p-4 rounded-xl bg-slate-850 border border-slate-700 space-y-1">
              <div className="text-amber-400 font-bold">Layer 2: History-Dependent FSM</div>
              <p className="text-[11px] text-slate-400 font-sans">
                If castling: verify King & Rook have 0 prior moves. If en passant: verify enemy pawn moved 2 squares in prior halfmove.
              </p>
            </div>

            <div className="text-amber-400 font-bold text-lg">↓</div>

            <div className="w-full p-4 rounded-xl bg-slate-850 border border-slate-700 space-y-1">
              <div className="text-amber-400 font-bold">Layer 4: King Safety Filter</div>
              <p className="text-[11px] text-slate-400 font-sans">
                Simulate candidate move on virtual board. Ensure player's own king is not left in check. Check if opponent king attacked (+).
              </p>
            </div>

            <div className="text-amber-400 font-bold text-lg">↓</div>

            <div className="w-full p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-center text-emerald-300 font-bold text-sm">
              ACCEPT: State Committed & Turn Toggled to Opponent
            </div>
          </div>
        </div>
      )}

      {/* Tab 6: College Viva Defense Q&A */}
      {activeTab === 'viva' && (
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
            <div className="border-b border-slate-800 pb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">Viva & Defense Readiness</span>
              <h3 className="text-2xl font-bold text-white mt-1">Theory of Computation Examination Guide</h3>
              <p className="text-xs text-slate-400 mt-1">
                High-yield viva questions with rigorous formal language explanations to ace college project evaluations.
              </p>
            </div>

            <div className="space-y-4">
              {vivaQuestions.map((item, idx) => (
                <div key={idx} className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="flex items-start space-x-3">
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono font-bold text-xs shrink-0 mt-0.5">
                      Q{idx + 1}
                    </span>
                    <h4 className="text-sm font-bold text-white">{item.q}</h4>
                  </div>
                  <p className="text-xs text-slate-300 pl-8 leading-relaxed">
                    {item.a}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
