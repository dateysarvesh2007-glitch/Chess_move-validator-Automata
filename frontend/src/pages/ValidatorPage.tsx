import React, { useState, useEffect } from 'react';
import { Chessboard } from 'react-chessboard';
import { 
  ShieldCheck, 
  RotateCcw, 
  Undo2, 
  Play, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Info, 
  Layers, 
  ArrowRightLeft,
  Copy,
  Check
} from 'lucide-react';
import { 
  createNewGame, 
  makeMove, 
  undoMove, 
  resetGame, 
  validateSequence 
} from '../services/api';
import type { 
  GameStateResponse, 
  MoveResponse, 
  LayerAnalysis 
} from '../services/api';

export const ValidatorPage: React.FC = () => {
  const [gameState, setGameState] = useState<GameStateResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [lastMove, setLastMove] = useState<{ from: string; to: string } | null>(null);
  const [latestValidation, setLatestValidation] = useState<{
    accepted: boolean;
    reason: string;
    move_notation: string;
    layer_analysis?: LayerAnalysis;
  } | null>(null);
  const [boardOrientation, setBoardOrientation] = useState<'white' | 'black'>('white');
  const [sequenceInput, setSequenceInput] = useState<string>('e4 e5 Nf3 Nc6 Bc4 Bc5');
  const [sequenceRunning, setSequenceRunning] = useState<boolean>(false);
  const [sequenceResult, setSequenceResult] = useState<string | null>(null);
  const [copiedFen, setCopiedFen] = useState<boolean>(false);

  // Initialize new game on component mount
  useEffect(() => {
    initGame();
  }, []);

  const initGame = async () => {
    try {
      setLoading(true);
      const data = await createNewGame();
      setGameState(data);
      setLastMove(null);
      setLatestValidation(null);
      setSelectedSquare(null);
      setSequenceResult(null);
    } catch (err) {
      console.error('Failed to init game', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSquareClick = (square: string) => {
    if (!gameState) return;

    if (!selectedSquare) {
      // First click: select piece if square is occupied by active player
      const pieceCode = gameState.board[square];
      if (pieceCode) {
        const pieceColor = pieceCode[0] === 'w' ? 'white' : 'black';
        if (pieceColor === gameState.current_turn) {
          setSelectedSquare(square);
        }
      }
    } else {
      // Second click: attempt move from selectedSquare to square
      if (selectedSquare === square) {
        setSelectedSquare(null);
      } else {
        const fromSq = selectedSquare;
        setSelectedSquare(null);
        executeMove(fromSq, square);
      }
    }
  };

  const executeMove = async (fromSquare: string, toSquare: string) => {
    if (!gameState) return;
    setActionLoading(true);

    try {
      const res: MoveResponse = await makeMove(gameState.game_id, fromSquare, toSquare);

      setLatestValidation({
        accepted: res.accepted,
        reason: res.reason,
        move_notation: res.move_notation,
        layer_analysis: res.layer_analysis,
      });

      if (res.accepted) {
        setGameState({
          game_id: gameState.game_id,
          current_turn: res.current_turn,
          fen: res.fen,
          board: res.board,
          is_check: res.is_check,
          move_count: res.move_history.length,
          castling_rights: gameState.castling_rights,
          move_history: res.move_history,
        });
        setLastMove({ from: fromSquare, to: toSquare });
      }
    } catch (err: any) {
      setLatestValidation({
        accepted: false,
        reason: err.message || 'Validation rejected by server',
        move_notation: `${fromSquare}->${toSquare}`,
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleUndo = async () => {
    if (!gameState || gameState.move_count === 0) return;
    setActionLoading(true);
    try {
      const res = await undoMove(gameState.game_id);
      if (res.success) {
        setGameState(res.game_state);
        setLatestValidation(null);
        setSelectedSquare(null);
        const history = res.game_state.move_history;
        if (history.length > 0) {
          const prev = history[history.length - 1];
          setLastMove({ from: prev.from_square, to: prev.to_square });
        } else {
          setLastMove(null);
        }
      }
    } catch (err) {
      console.error('Undo failed', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReset = async () => {
    if (!gameState) return;
    setActionLoading(true);
    try {
      const res = await resetGame(gameState.game_id);
      setGameState(res);
      setLatestValidation(null);
      setLastMove(null);
      setSelectedSquare(null);
      setSequenceResult(null);
    } catch (err) {
      console.error('Reset failed', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRunSequence = async () => {
    if (!sequenceInput.trim()) return;
    setSequenceRunning(true);
    setSequenceResult(null);

    try {
      const tokens = sequenceInput.trim().split(/\s+/);
      const res = await validateSequence(tokens);

      if (res.valid) {
        setSequenceResult(`Valid Sequence! All ${res.total_moves} moves accepted by 4-layer engine.`);
        // Reload current game to match final FEN
        await handleReset();
      } else {
        setSequenceResult(`Sequence REJECTED at move ${res.processed_moves + 1} (${res.error_move}): ${res.error_reason}`);
      }
    } catch (err: any) {
      setSequenceResult(`Error: ${err.message}`);
    } finally {
      setSequenceRunning(false);
    }
  };

  const copyFen = () => {
    if (gameState?.fen) {
      navigator.clipboard.writeText(gameState.fen);
      setCopiedFen(true);
      setTimeout(() => setCopiedFen(false), 2000);
    }
  };

  // Custom square styles for highlights
  const customSquareStyles: Record<string, React.CSSProperties> = {};
  if (selectedSquare) {
    customSquareStyles[selectedSquare] = {
      backgroundColor: 'rgba(245, 158, 11, 0.45)',
      boxShadow: 'inset 0 0 0 3px #f59e0b',
    };
  }
  if (lastMove) {
    customSquareStyles[lastMove.from] = {
      backgroundColor: 'rgba(217, 119, 6, 0.25)',
    };
    customSquareStyles[lastMove.to] = {
      backgroundColor: 'rgba(245, 158, 11, 0.35)',
    };
  }

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-amber-500/30 border-t-amber-400 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Connecting to Python Automata Validation Engine...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Title & Status Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Interactive Validation Dashboard</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Live Chess Move Legality Checker
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Every movement request is dispatched to the Python backend to verify DFA line-of-sight, FSM history tape, and lookahead check safety.
          </p>
        </div>

        {/* Turn & Check Notification */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-3 px-4 py-2.5 rounded-xl bg-[#111a2e] border border-slate-800 shadow-md">
            <div className={`w-3.5 h-3.5 rounded-full ${gameState?.current_turn === 'white' ? 'bg-slate-100 ring-2 ring-slate-400/50' : 'bg-slate-900 ring-2 ring-slate-600'}`} />
            <div>
              <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Active Turn</div>
              <div className="text-sm font-bold text-white capitalize">{gameState?.current_turn} to move</div>
            </div>
          </div>

          {gameState?.is_check && (
            <div className="flex items-center space-x-1.5 px-3 py-2.5 rounded-xl bg-red-500/15 border border-red-500/40 text-red-400 text-xs font-bold animate-pulse">
              <AlertTriangle className="w-4 h-4" />
              <span>KING IN CHECK!</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Grid: Chessboard (Left) + Validation Analysis (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Chessboard Column (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-[#111a2e] p-4 sm:p-6 rounded-2xl border border-slate-800/80 shadow-2xl flex flex-col items-center">
            <div className="w-full max-w-[500px] aspect-square relative rounded-xl overflow-hidden shadow-2xl border-2 border-slate-700/60">
              {gameState && (
                <Chessboard
                  options={{
                    position: gameState.fen,
                    onPieceDrop: ({ sourceSquare, targetSquare }) => {
                      if (!targetSquare || sourceSquare === targetSquare) {
                        setSelectedSquare(null);
                        return false;
                      }
                      executeMove(sourceSquare, targetSquare);
                      return true;
                    },
                    onSquareClick: ({ square }) => {
                      handleSquareClick(square);
                    },
                    boardOrientation: boardOrientation,
                    squareStyles: customSquareStyles,
                    darkSquareStyle: { backgroundColor: '#b58863' },
                    lightSquareStyle: { backgroundColor: '#f0d9b5' },
                    animationDurationInMs: 200,
                  }}
                />
              )}
            </div>

            {/* Board Controls */}
            <div className="w-full max-w-[500px] mt-5 flex items-center justify-between gap-2 text-xs">
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleUndo}
                  disabled={actionLoading || !gameState || gameState.move_count === 0}
                  className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 font-medium transition-colors"
                >
                  <Undo2 className="w-3.5 h-3.5 text-amber-400" />
                  <span>Undo</span>
                </button>
                <button
                  onClick={handleReset}
                  disabled={actionLoading}
                  className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 font-medium transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
                  <span>Reset Board</span>
                </button>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setBoardOrientation(boardOrientation === 'white' ? 'black' : 'white')}
                  className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-850 hover:bg-slate-800 text-slate-300 font-medium border border-slate-700 transition-colors"
                >
                  <ArrowRightLeft className="w-3.5 h-3.5 text-slate-400" />
                  <span className="capitalize">{boardOrientation === 'white' ? 'Flip to Black' : 'Flip to White'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Current FEN / State String Bar */}
          <div className="bg-[#111a2e]/60 border border-slate-800 rounded-xl p-3 flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2 overflow-hidden mr-2">
              <span className="font-mono font-bold text-amber-400 shrink-0">FEN:</span>
              <span className="font-mono text-slate-400 truncate">{gameState?.fen}</span>
            </div>
            <button
              onClick={copyFen}
              className="flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 shrink-0 transition-colors"
            >
              {copiedFen ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedFen ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
        </div>

        {/* Validation Output & 4-Layer Diagnostics (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Real-Time Move Legality Result Card */}
          <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Move Legality Verdict
              </span>
              {latestValidation ? (
                latestValidation.accepted ? (
                  <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>ACCEPTED</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-red-500/15 border border-red-500/30 text-red-400 text-xs font-bold">
                    <XCircle className="w-3.5 h-3.5" />
                    <span>REJECTED</span>
                  </span>
                )
              ) : (
                <span className="text-xs text-slate-500">Awaiting Move</span>
              )}
            </div>

            {latestValidation ? (
              <div className="space-y-3">
                <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wide">
                    Engine Explanation
                  </div>
                  <div className="text-sm font-semibold text-white mt-1">
                    {latestValidation.reason}
                  </div>
                  {latestValidation.move_notation && (
                    <div className="text-xs text-amber-400 font-mono mt-1">
                      Notation: {latestValidation.move_notation}
                    </div>
                  )}
                </div>

                {/* Four Layers Detailed Breakdown */}
                {latestValidation.layer_analysis && (
                  <div className="space-y-2 pt-2">
                    <div className="text-xs font-bold text-slate-300 flex items-center space-x-1.5">
                      <Layers className="w-3.5 h-3.5 text-amber-400" />
                      <span>Four-Layer Automata Diagnostic</span>
                    </div>

                    {/* Layer 1 */}
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs flex items-start space-x-2">
                      <div className="mt-0.5">
                        {latestValidation.layer_analysis.layer1.passed ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold text-white">
                          Layer 1: Piece DFA
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          {latestValidation.layer_analysis.layer1.details}
                        </div>
                      </div>
                    </div>

                    {/* Layer 2 */}
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs flex items-start space-x-2">
                      <div className="mt-0.5">
                        {latestValidation.layer_analysis.layer2.passed ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold text-white">
                          Layer 2: History FSM
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          {latestValidation.layer_analysis.layer2.details}
                        </div>
                      </div>
                    </div>

                    {/* Layer 3 */}
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs flex items-start space-x-2">
                      <div className="mt-0.5">
                        {latestValidation.layer_analysis.layer3.passed ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold text-white">
                          Layer 3: Turn & Sequencer
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          {latestValidation.layer_analysis.layer3.details}
                        </div>
                      </div>
                    </div>

                    {/* Layer 4 */}
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs flex items-start space-x-2">
                      <div className="mt-0.5">
                        {latestValidation.layer_analysis.layer4.passed ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold text-white">
                          Layer 4: Safety & Check Filter
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          {latestValidation.layer_analysis.layer4.details}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-8 text-center text-slate-500 space-y-2">
                <Info className="w-8 h-8 mx-auto text-slate-600" />
                <p className="text-xs">Drag any piece or click a square to test move legality in real time.</p>
              </div>
            )}
          </div>

          {/* Move History Log */}
          <div className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Move History ({gameState?.move_history.length || 0})
              </span>
              <span className="text-[11px] font-mono text-amber-400">
                Chronological State Tape
              </span>
            </div>

            <div className="max-h-48 overflow-y-auto pr-1 space-y-1.5 text-xs font-mono">
              {gameState?.move_history && gameState.move_history.length > 0 ? (
                gameState.move_history.map((m) => (
                  <div
                    key={m.move_number}
                    className="flex items-center justify-between p-2 rounded bg-slate-900/70 border border-slate-800/80"
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-500 w-6">{m.move_number}.</span>
                      <span className={`font-semibold capitalize ${m.color === 'white' ? 'text-slate-200' : 'text-amber-400'}`}>
                        {m.color}
                      </span>
                      <span className="text-slate-300">
                        {m.from_square} → {m.to_square}
                      </span>
                      <span className="text-[10px] text-slate-500">({m.piece})</span>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      {m.is_capture && (
                        <span className="px-1.5 py-0.2 rounded bg-red-500/20 text-red-300 text-[10px]">
                          x {m.captured || 'piece'}
                        </span>
                      )}
                      {m.is_en_passant && (
                        <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[10px]">
                          e.p.
                        </span>
                      )}
                      {m.is_promotion && (
                        <span className="px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 text-[10px]">
                          =Q
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-slate-500 text-xs">
                  No moves played yet. Initial position.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Batch Game Sequence Verification Box */}
      <section className="bg-[#111a2e] border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl">
        <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">
          <Play className="w-4 h-4" />
          <span>Layer 3 Sequence Engine</span>
        </div>
        <h3 className="text-lg font-bold text-white">
          Validate Ordered Move Sequence
        </h3>
        <p className="text-xs text-slate-400 mt-1 max-w-2xl">
          Enter a whitespace-separated sequence of standard algebraic moves (e.g. <code>e4 e5 Nf3 Nc6 Bc4 Bc5</code>).
          The validator evaluates each move chronologically, halting and identifying the exact violating move if illegal.
        </p>

        <div className="mt-4 flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={sequenceInput}
            onChange={(e) => setSequenceInput(e.target.value)}
            placeholder="e4 e5 Nf3 Nc6 Bc4 Bc5"
            className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white font-mono placeholder:text-slate-600 focus:outline-none focus:border-amber-500/80 transition-colors"
          />
          <button
            onClick={handleRunSequence}
            disabled={sequenceRunning || !sequenceInput.trim()}
            className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold text-sm shrink-0 flex items-center justify-center space-x-2 transition-colors shadow-md shadow-amber-500/10"
          >
            {sequenceRunning ? (
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-current" />
            )}
            <span>Validate Sequence</span>
          </button>
        </div>

        {sequenceResult && (
          <div className={`mt-4 p-4 rounded-xl border text-xs font-mono ${
            sequenceResult.startsWith('Valid')
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              : 'bg-red-500/10 border-red-500/30 text-red-300'
          }`}>
            {sequenceResult}
          </div>
        )}
      </section>
    </div>
  );
};
