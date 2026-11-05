import { describe, it, expect, vi, beforeEach } from 'vitest';
import { 
  createNewGame, 
  makeMove, 
  undoMove, 
  validateSequence,
  fetchAutomataLayers,
  fetchDatasetSamples
} from './api';

describe('ChessMove Validator Frontend API Service', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('createNewGame dispatches POST to /api/game/new', async () => {
    const mockData = {
      game_id: 'test-123',
      current_turn: 'white',
      fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
      board: {},
      is_check: false,
      move_count: 0,
      castling_rights: { white: { kingside: true, queenside: true }, black: { kingside: true, queenside: true } },
      move_history: []
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    } as Response);

    const res = await createNewGame();
    expect(res.game_id).toBe('test-123');
    expect(res.current_turn).toBe('white');
    expect(globalThis.fetch).toHaveBeenCalledWith(expect.stringContaining('/api/game/new'), expect.any(Object));
  });

  it('makeMove sends source and destination coordinates to backend', async () => {
    const mockMoveResp = {
      accepted: true,
      reason: 'Legal pawn advance',
      move_notation: 'e4',
      is_check: false,
      is_checkmate: false,
      current_turn: 'black',
      fen: 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
      board: {},
      move_history: [],
      layer_analysis: {
        layer1: { name: 'Layer 1: DFA', passed: true, status: 'ACCEPTED', details: 'Passed' },
        layer2: { name: 'Layer 2: FSM', passed: true, status: 'NOT_APPLICABLE', details: 'N/A' },
        layer3: { name: 'Layer 3: FSM', passed: true, status: 'ACCEPTED', details: 'Turn ok' },
        layer4: { name: 'Layer 4: Safety', passed: true, status: 'ACCEPTED', details: 'King safe' }
      }
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockMoveResp,
    } as Response);

    const res = await makeMove('test-123', 'e2', 'e4');
    expect(res.accepted).toBe(true);
    expect(res.current_turn).toBe('black');
    expect(res.layer_analysis.layer1.passed).toBe(true);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/game/move'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ game_id: 'test-123', from_square: 'e2', to_square: 'e4', promotion: undefined })
      })
    );
  });

  it('undoMove sends undo request', async () => {
    const mockUndoResp = {
      success: true,
      message: 'Previous move undone',
      game_state: {
        game_id: 'test-123',
        current_turn: 'white',
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        board: {},
        is_check: false,
        move_count: 0,
        castling_rights: { white: { kingside: true, queenside: true }, black: { kingside: true, queenside: true } },
        move_history: []
      }
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockUndoResp,
    } as Response);

    const res = await undoMove('test-123');
    expect(res.success).toBe(true);
    expect(res.game_state.move_count).toBe(0);
  });

  it('validateSequence calls /api/game/validate-sequence', async () => {
    const mockSeqResp = {
      valid: true,
      total_moves: 4,
      processed_moves: 4,
      final_fen: '...',
      final_turn: 'white',
      steps: []
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockSeqResp,
    } as Response);

    const res = await validateSequence(['e4', 'e5', 'Nf3', 'Nc6']);
    expect(res.valid).toBe(true);
    expect(res.processed_moves).toBe(4);
  });

  it('fetchAutomataLayers fetches layer specifications', async () => {
    const mockLayers = {
      total_layers: 4,
      layers: [
        { id: 'layer1', name: 'Layer 1: Piece DFA' },
        { id: 'layer2', name: 'Layer 2: History FSM' },
        { id: 'layer3', name: 'Layer 3: Sequence FSM' },
        { id: 'layer4', name: 'Layer 4: Safety Filter' }
      ]
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockLayers,
    } as Response);

    const res = await fetchAutomataLayers();
    expect(res.total_layers).toBe(4);
    expect(res.layers.length).toBe(4);
  });

  it('fetchDatasetSamples retrieves sample list', async () => {
    const mockSamples = {
      samples: [
        { id: 'game-1', title: 'The Opera Game', category: 'legal', move_count: 33 },
        { id: 'neg-1', title: 'Self-Check Negative Test', category: 'illegal', move_count: 9 }
      ]
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockSamples,
    } as Response);

    const res = await fetchDatasetSamples();
    expect(res.samples.length).toBe(2);
    expect(res.samples[0].id).toBe('game-1');
  });
});
