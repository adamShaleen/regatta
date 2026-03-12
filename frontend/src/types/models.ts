import { Dispatch, SetStateAction } from 'react';
import type { components } from '../types/api';

export type GameResponse = components['schemas']['GameResponse'] & { last_event: string | null };
export type BoardResponse = components['schemas']['BoardResponse'];
export type YachtResponse = components['schemas']['YachtResponse'];

export interface PhaseProps {
  game: GameResponse;
  setGame: Dispatch<SetStateAction<GameResponse | undefined>>;
  playerId: string | null;
}
