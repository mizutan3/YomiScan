import * as FileSystem from 'expo-file-system';
import * as Sharing from "expo-sharing";
import { HistoryEntry } from '../models/types';

const HISTORY_FILE = `${FileSystem.documentDirectory}history.json`;

export const loadHistory = async (): Promise<HistoryEntry[]> => {
  try {
    const savedHistory = await FileSystem.readAsStringAsync(HISTORY_FILE);
    return savedHistory ? JSON.parse(savedHistory) : [];
  } catch (error) {
    console.warn("History not found or corrupted. Returning empty.");
    return [];
  }
};

export const addToHistory = async (
  word: string,
  reading: string,
  definition: string,
  history: HistoryEntry[],
  setHistory: (history: HistoryEntry[]) => void
): Promise<void> => {
  const timestamp = Date.now();
  const newEntry: HistoryEntry = {
    word,
    reading,
    definition,
    timestamp: formatTimestamp(timestamp),
    rawTimestamp: timestamp
  };
  
  const filteredHistory = history.filter(entry => entry.word !== word);
  const updatedHistory = [newEntry, ...filteredHistory].slice(0, 100);
  
  setHistory(updatedHistory);

  try {
    await FileSystem.writeAsStringAsync(
      HISTORY_FILE,
      JSON.stringify(updatedHistory, null, 2),
      { encoding: FileSystem.EncodingType.UTF8 }
    );
  } catch (error) {
    console.error('Failed to save history to file:', error);
  }
};

export const exportHistory = async (history: HistoryEntry[]): Promise<void> => {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_');
    const filename = `yomiscan-history-${timestamp}.json`;
    const fileUri = `${FileSystem.cacheDirectory}${filename}`;
    
    await FileSystem.writeAsStringAsync(
      fileUri,
      JSON.stringify(history, null, 2),
      { encoding: FileSystem.EncodingType.UTF8 }
    );

    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(fileUri, {
        mimeType: 'application/json',
        dialogTitle: 'Share History Export',
        UTI: 'public.json'
      });
    } else {
      throw new Error('Sharing not available');
    }
  } catch (error) {
    console.error('Export error:', error);
    throw error;
  }
};

export const clearHistory = async (
  setHistory: (history: HistoryEntry[]) => void
): Promise<void> => {
  try {
    await FileSystem.deleteAsync(HISTORY_FILE, { idempotent: true });
    setHistory([]);
  } catch (error) {
    console.error('Failed to clear history', error);
    throw error;
  }
};

const formatTimestamp = (timestamp: number): string => {
  const date = new Date(timestamp);
  return date.toLocaleString();
};
