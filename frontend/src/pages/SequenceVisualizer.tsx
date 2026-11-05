import React, { useState } from 'react';
import { Chessboard } from 'react-chessboard';
import { Check, XCircle, ArrowRightLeft, RefreshCcw } from 'lucide-react';
import { validateSequence, resetGame } from '../services/api';
import type { SequenceValidateResponse, SequenceStep, GameStateResponse } from '../services/api';

export const SequenceVisualizer: React.FC = () => {
  const [input, setInput] = useState('e4 e5 Nf3 Nc6');
  const [steps, setSteps] = useState<SequenceStep[]>([]);
  const [currentIdx, setCurrentIdx] = useState<number>(-1);
  const [boardPos, setBoardPos] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startVisualization = async () => {
    setLoading(true);
    setError(null);
    try {
      const moves = input.trim().split(/\s+/);
      const res: SequenceValidateResponse = await validateSequence(moves);
      if (!res.valid && res.error_move) {
        setError(`Sequence rejected at move ${res.error_move}: ${res.error_reason}`);
      }
      setSteps(res.steps);
      // Reset backend game to start from empty board
      const dummyGameId = 'seq-vis-' + Date.now();
      const newGame: GameStateResponse = await resetGame(dummyGameId);
      setBoardPos(newGame.fen);
      setCurrentIdx(0);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const applyStep = (idx: number) => {
    const step = steps[idx];
    setBoardPos(step.fen_after);
    setCurrentIdx(idx);
  };

  const next = () => {
    if (currentIdx + 1 < steps.length) applyStep(currentIdx + 1);
  };
  const prev = () => {
    if (currentIdx - 1 >= 0) applyStep(currentIdx - 1);
  };

  const reset = async () => {
    setSteps([]);
    setCurrentIdx(-1);
    setBoardPos('');
    setInput('e4 e5 Nf3 Nc6');
    setError(null);
  };

  return (
    <div className="p-6 bg-background min-h-screen text-primary">
      <h2 className="text-2xl font-bold mb-4">Sequence Visualizer</h2>
      <div className="mb-4">
        <textarea
          className="w-full p-2 rounded border focus:outline-none focus:ring-2 focus:ring-accent"
          rows={2}
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Enter moves in algebraic notation separated by spaces"
        />
      </div>
      <div className="flex gap-2 mb-4">
        <button
          className="px-4 py-2 bg-success text-white rounded hover:bg-success/80 flex items-center"
          onClick={startVisualization}
          disabled={loading}
        >
          <ArrowRightLeft className="mr-2" size={18} />
          Visualize
        </button>
        <button
          className="px-4 py-2 bg-secondary text-primary rounded hover:bg-secondary/80 flex items-center"
          onClick={reset}
        >
          <RefreshCcw className="mr-2" size={18} />
          Reset
        </button>
      </div>
      {error && (
        <div className="mb-2 text-danger flex items-center">
          <XCircle className="mr-1" size={18} /> {error}
        </div>
      )}
      {boardPos && (
        <div className="flex flex-col items-center">
          <Chessboard
  		options={{
    			position: boardPos,
    			boardOrientation: 'white',
    			boardStyle: {
      				borderRadius: '0.75rem',
      				overflow: 'hidden',
    			},
  		}}
	/>
          {steps.length > 0 && (
            <div className="mt-4 flex gap-4 items-center">
              <button
                className="px-3 py-1 bg-primary text-white rounded disabled:opacity-50"
                onClick={prev}
                disabled={currentIdx <= 0}
              >
                Prev
              </button>
              <span>
                Step {currentIdx + 1} / {steps.length}
                {steps[currentIdx]?.accepted ? (
                  <Check className="inline ml-1 text-success" size={16} />
                ) : (
                  <XCircle className="inline ml-1 text-danger" size={16} />
                )}
              </span>
              <button
                className="px-3 py-1 bg-primary text-white rounded disabled:opacity-50"
                onClick={next}
                disabled={currentIdx + 1 >= steps.length}
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
