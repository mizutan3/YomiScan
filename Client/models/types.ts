// models/types.ts

import { Card } from "ts-fsrs";

export interface HistoryEntry {
    word: string;
    reading: string;
    definition: string;
    timestamp: string;
    rawTimestamp: number;
}

export interface DictionaryInfo {
    name: string;
    loaded: boolean;
    position: number;
    loading?: boolean;
    error?: string;
}

export interface Flashcard {
    card: Card;
    word: string;
    reading: string;
    definition: string;
}

export interface Deck {
    name: string;
    cards: Flashcard[];
}
