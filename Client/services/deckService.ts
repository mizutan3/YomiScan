// src/services/deckService.ts
import * as FileSystem from 'expo-file-system';
import { Deck, Flashcard  } from '../models/types';
import { 
    Card, 
    createEmptyCard, 
    generatorParameters, 
    FSRS, 
    RecordLog, 
    RecordLogItem,
    Rating,
    State
  } from "ts-fsrs";
  import * as Sharing from 'expo-sharing';


  const DECKS_FILE = `${FileSystem.documentDirectory}decks.json`;

  export const loadDecks = async (): Promise<Deck[]> => {
    try {
      const savedDecks = await FileSystem.readAsStringAsync(DECKS_FILE);
  
      if (!savedDecks) {
        throw new Error("Empty decks file");
      }
  
      const parsed = JSON.parse(savedDecks);
      if (!Array.isArray(parsed)) throw new Error("Decks data is invalid");
  
      return parsed;
    } catch (error) {
      console.warn("Decks not found or corrupted. Returning empty.");
      return [];
    }
  };
  
  export const saveDecks = async (decks: Deck[]): Promise<void> => {
    try {
      await FileSystem.writeAsStringAsync(
        DECKS_FILE,
        JSON.stringify(decks, null, 2),
        { encoding: FileSystem.EncodingType.UTF8 }
      );
    } catch (error) {
      console.error('Failed to save decks to file:', error);
    }
  };

  export const exportDeck = async (deck: Deck): Promise<void> => {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_');
      const filename = `fsrs-deck-${deck.name}-${timestamp}.json`;
      const fileUri = `${FileSystem.cacheDirectory}${filename}`;
  
      const exportData = {
        name: deck.name,
        cards: deck.cards.map(card => ({
          ...card,
          card: {
            ...card.card,
            due: new Date(card.card.due).toISOString(), 
          }
        }))
      };
  
      await FileSystem.writeAsStringAsync(fileUri, JSON.stringify(exportData, null, 2));
  
      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(fileUri, {
          mimeType: 'application/json',
          dialogTitle: `Export "${deck.name}" Deck`,
          UTI: 'public.json',
        });
      } else {
        throw new Error('Sharing is not available on this device');
      }
    } catch (error) {
      console.error('Failed to export deck:', error);
      throw error;
    }
  };

export const deleteCardFromDeck = async (
    deckIndex: number,
    cardIndex: number,
    decks: Deck[],
    setDecks: (decks: Deck[]) => void
  ): Promise<void> => {
    try {
      const updatedDecks = [...decks];
      updatedDecks[deckIndex].cards.splice(cardIndex, 1);
      
      setDecks(updatedDecks);
      await saveDecks(updatedDecks);
    } catch (error) {
      console.error('Error deleting card:', error);
      throw error;
    }
  };
  
  export const addCardToDeck = async (
    deckIndex: number,
    word: string,
    reading: string,
    definition: string,
    decks: Deck[],
    setDecks: (decks: Deck[]) => void
  ): Promise<void> => {
    // Check if word already exists in deck
    const existingCard = decks[deckIndex].cards.find(
      card => card.word === word && card.reading === reading
    );
    
    if (existingCard) {
      throw new Error("This word is already in the deck");
    }
  
    const newCard: Flashcard = {
      card: createEmptyCard(),
      word,
      reading,
      definition
    };
  
    const updatedDecks = [...decks];
    updatedDecks[deckIndex].cards.push(newCard);
    
    setDecks(updatedDecks);
    await saveDecks(updatedDecks);
  };
  
  export const deleteDeck = async (
    deckIndex: number,
    decks: Deck[],
    currentDeckIndex: number,
    setDecks: (decks: Deck[]) => void,
    setCurrentDeckIndex: (index: number) => void,
    setIsViewingDeck: (viewing: boolean) => void
  ): Promise<void> => {
    try {
      const updatedDecks = [...decks];
      updatedDecks.splice(deckIndex, 1);
      
      if (currentDeckIndex === deckIndex) {
        setCurrentDeckIndex(0);
      } else if (currentDeckIndex > deckIndex) {
        setCurrentDeckIndex(currentDeckIndex - 1);
      }
      
      setDecks(updatedDecks);
      await saveDecks(updatedDecks);
      
      setIsViewingDeck(false);
    } catch (error) {
      console.error('Error deleting deck:', error);
      throw error;
    }
  };
  
  export const createNewDeck = async (
    newDeckName: string,
    decks: Deck[],
    setDecks: (decks: Deck[]) => void,
    setNewDeckName: (name: string) => void,
    setIsCreateDeckModalVisible: (visible: boolean) => void
  ): Promise<void> => {
    if (!newDeckName.trim()) {
      throw new Error("Deck name cannot be empty");
    }
  
    const newDeck: Deck = {
      name: newDeckName.trim(),
      cards: []
    };
  
    const updatedDecks = [...decks, newDeck];
    setDecks(updatedDecks);
    await saveDecks(updatedDecks);
    
    setNewDeckName('');
    setIsCreateDeckModalVisible(false);
  };