const BASE_URL = import.meta.env.VITE_API_URL || '';

export interface LayerDetail {
  name: string;
  passed: boolean;
  status: 'ACCEPTED' | 'REJECTED' | 'NOT_APPLICABLE';
  details: string;
}

export interface LayerAnalysis {
  layer1: LayerDetail;
  layer2: LayerDetail;
  layer3: LayerDetail;
  layer4: LayerDetail;
}

export interface MoveRecord {
  move_number: number;
  from_square: string;
  to_square: string;
  piece: string;
  color: string;
  notation: string;
  is_check: boolean;
  is_capture: boolean;
  is_en_passant: boolean;
  is_promotion: boolean;
  captured?: string | null;
}

export interface GameStateResponse {
  game_id: string;
  current_turn: 'white' | 'black';
  fen: string;
  board: Record<string, string>;
  is_check: boolean;
  move_count: number;
  castling_rights: {
    white: { kingside: boolean; queenside: boolean };
    black: { kingside: boolean; queenside: boolean };
  };
  en_passant_target?: string | null;
  move_history: MoveRecord[];
  message?: string;
}

export interface MoveResponse {
  accepted: boolean;
  reason: string;
  move_notation: string;
  is_check: boolean;
  is_checkmate: boolean;
  current_turn: 'white' | 'black';
  fen: string;
  board: Record<string, string>;
  move_history: MoveRecord[];
  layer_analysis: LayerAnalysis;
}

export interface UndoResponse {
  success: boolean;
  message: string;
  game_state: GameStateResponse;
}

export interface SequenceStep {
  move_index: number;
  turn: string;
  move: string;
  accepted: boolean;
  reason: string;
  is_check: boolean;
  fen_after: string;
}

export interface SequenceValidateResponse {
  valid: boolean;
  total_moves: number;
  processed_moves: number;
  final_fen: string;
  final_turn: string;
  steps: SequenceStep[];
  error_move?: string | null;
  error_reason?: string | null;
}

export interface DatasetSample {
  id: string;
  title: string;
  white: string;
  black: string;
  result: string;
  move_count: number;
  category: 'legal' | 'illegal';
  description: string;
}

export interface DatasetGameResult {
  id: string;
  title: string;
  total_moves: number;
  processed_moves: number;
  status: 'ACCEPTED' | 'REJECTED';
  reason?: string;
  failing_move?: string;
  metadata: Record<string, string>;
}

export interface DatasetValidateResponse {
  dataset_name: string;
  total_games: number;
  accepted_games: number;
  rejected_games: number;
  total_moves: number;
  games: DatasetGameResult[];
}

export interface LayerMetadata {
  id: string;
  name: string;
  formal_definition: string;
  description: string;
  states: string[];
  alphabet: string[];
  accepting_condition: string;
  rejecting_condition: string;
  pieces?: string[];
  subsystems?: Array<{ name: string; rules: string[] }>;
}

export interface PieceDFASpec {
  piece: string;
  states: string[];
  transition_table: Array<{ from: string; input: string; to: string }>;
  viva_insight: string;
}

// API methods
export async function createNewGame(gameId?: string): Promise<GameStateResponse> {
  const url = gameId ? `${BASE_URL}/api/game/new?game_id=${gameId}` : `${BASE_URL}/api/game/new`;
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create new game');
  return res.json();
}

export async function fetchGameState(gameId: string): Promise<GameStateResponse> {
  const res = await fetch(`${BASE_URL}/api/game/${gameId}`);
  if (!res.ok) throw new Error('Failed to fetch game state');
  return res.json();
}

export async function makeMove(
  gameId: string,
  fromSquare: string,
  toSquare: string,
  promotion?: string
): Promise<MoveResponse> {
  const res = await fetch(`${BASE_URL}/api/game/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      game_id: gameId,
      from_square: fromSquare,
      to_square: toSquare,
      promotion,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to validate move' }));
    throw new Error(err.detail || 'Move validation failed');
  }
  return res.json();
}

export async function undoMove(gameId: string): Promise<UndoResponse> {
  const res = await fetch(`${BASE_URL}/api/game/undo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ game_id: gameId }),
  });
  if (!res.ok) throw new Error('Undo request failed');
  return res.json();
}

export async function resetGame(gameId: string): Promise<GameStateResponse> {
  const res = await fetch(`${BASE_URL}/api/game/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ game_id: gameId }),
  });
  if (!res.ok) throw new Error('Reset request failed');
  return res.json();
}

export async function validateSequence(moves: string[]): Promise<SequenceValidateResponse> {
  const res = await fetch(`${BASE_URL}/api/game/validate-sequence`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ moves }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Validation failed' }));
    throw new Error(err.detail || 'Sequence validation failed');
  }
  return res.json();
}

export async function fetchAutomataLayers(): Promise<{ total_layers: number; layers: LayerMetadata[] }> {
  const res = await fetch(`${BASE_URL}/api/automata/layers`);
  if (!res.ok) throw new Error('Failed to load automata layers');
  return res.json();
}

export async function fetchPieceDFAs(): Promise<Record<string, PieceDFASpec>> {
  const res = await fetch(`${BASE_URL}/api/automata/pieces`);
  if (!res.ok) throw new Error('Failed to load piece DFAs');
  return res.json();
}

export async function fetchDatasetSamples(): Promise<{ samples: DatasetSample[] }> {
  const res = await fetch(`${BASE_URL}/api/dataset/samples`);
  if (!res.ok) throw new Error('Failed to load dataset samples');
  return res.json();
}

export async function runDatasetValidation(options: {
  sample_id?: string;
  pgn_content?: string;
  test_type?: string;
}): Promise<DatasetValidateResponse> {
  const res = await fetch(`${BASE_URL}/api/dataset/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Dataset test failed' }));
    throw new Error(err.detail || 'Dataset validation failed');
  }
  return res.json();
}
