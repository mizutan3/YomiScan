// src/hooks/useAppState.ts
import { useState, useRef, useEffect } from 'react';
import { 
  loadHistory,
  addToHistory,
  exportHistory as exportHistoryService,
  clearHistory as clearHistoryService
} from '../services/historyService';
import { loadDecks, saveDecks } from '../services/deckService';
import { loadDictionaries } from '../services/dictionaryService';
import * as ImagePicker from 'expo-image-picker';
import {Animated, Alert, Platform} from "react-native";
import { HistoryEntry, DictionaryInfo, Deck, Flashcard } from '../models/types';
import { Audio } from 'expo-av';
import { initializeServerDictionaries } from '.././services/syncService';
import * as Device from 'expo-device';

export const useAppState = () => {
  const [image, setImage] = useState<string | null>(null);
  const [text, setText] = useState<string>("");
  const [words, setWords] = useState<string[]>([]);
  const [currentWord, setCurrentWord] = useState("");
  const [currentReading, setCurrentReading] = useState("");
  const [definition, setDefinition] = useState<string>("");
  const [definitionImages, setDefinitionImages] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isVertical, setIsVertical] = useState<boolean>(false);
  const [isDefinitionModalVisible, setIsDefinitionModalVisible] = useState<boolean>(false);
  const [isSidebarVisible, setIsSidebarVisible] = useState<boolean>(false);
  const [isDictionaryManagerVisible, setIsDictionaryManagerVisible] = useState<boolean>(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [dictionaries, setDictionaries] = useState<DictionaryInfo[]>([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [currentDeckIndex, setCurrentDeckIndex] = useState<number>(0);
  const [isReviewing, setIsReviewing] = useState<boolean>(false);
  const [currentReviewCard, setCurrentReviewCard] = useState<Flashcard | null>(null);
  const [showAnswer, setShowAnswer] = useState<boolean>(false);
  const [isViewingDeck, setIsViewingDeck] = useState<boolean>(false);
  const [viewingDeckIndex, setViewingDeckIndex] = useState<number>(0);
  const [isFastMode, setIsFastMode] = useState<boolean>(true);
  const [cropStart, setCropStart] = useState({ x: 0, y: 0 });
  const [cropEnd, setCropEnd] = useState({ x: 0, y: 0 });
  const [cropping, setCropping] = useState(false);
  const [currentMode, setCurrentMode] = useState<'ocr' | 'dictionary' | 'srs'>('ocr');
  const [dictionaryWordList, setDictionaryWordList] = useState<string[]>([]);
  const [isViewingDeckWords, setIsViewingDeckWords] = useState<boolean>(false);
  const [newDeckName, setNewDeckName] = useState('');
  const [isCreateDeckModalVisible, setIsCreateDeckModalVisible] = useState(false);
  const [isAudioInitialized, setIsAudioInitialized] = useState(false);
  const [kanjiComponents, setKanjiComponents] = useState<{kanji: string, reading: string}[]>([]);

  const sidebarAnimation = useRef(new Animated.Value(-300)).current;

  useEffect(() => {
    const checkDeviceCompatibility = async () => {
      try {
        // Перевірка версії ОС
        if (Platform.OS === 'android' && Platform.Version < 26) { // якщо версія нижча ніж Android 8.0 (API 26) 
          Alert.alert( // вивід повідомлення про помилку
            'Unsupported Android Version',
            'This app requires Android 8.0 (API 26) or later',
            [{ text: 'OK', onPress: () => {} }]
          );
        } else if (Platform.OS === 'ios') {
          const majorVersion = parseInt(Device.osVersion?.split('.')[0] || '0', 10); // якщо версія нижча ніж iOS 13
          if (majorVersion < 13) {
            Alert.alert(
              'Unsupported iOS Version',
              'This app requires iOS 13 or later',
              [{ text: 'OK', onPress: () => {} }]
            );
          }
        }

        // перевірка приблизного розміру пам'ятті
        if ((Device.totalMemory || 0) < 2000000000) { // 2 ГБ в байтах
          Alert.alert(
            'Insufficient Memory',
            'This app requires at least 2GB of RAM for optimal performance',
            [{ text: 'OK', onPress: () => {} }]
          );
        }
      } catch (error) {
        console.error('Device compatibility check failed:', error);
      }
    };
    const initializeApp = async () => {
      try {
        console.log("Initializing app...");

        await checkDeviceCompatibility();
  
        // Set up audio
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
          playsInSilentModeIOS: true,
          shouldDuckAndroid: true,
          staysActiveInBackground: false,
          playThroughEarpieceAndroid: false,
        });
        setIsAudioInitialized(true);
  
        const initializeLocalData = async () => {
          const loadedHistory = await loadHistory();
          setHistory(loadedHistory);
    
          const loadedDecks = await loadDecks();
          setDecks(loadedDecks);
        };
        initializeLocalData();

        // Load other local data
        const [loadedHistory, loadedDictionaries] = await Promise.all([
          loadHistory(),
          loadDictionaries()
        ]);
  
        setHistory(loadedHistory);
        setDictionaries(loadedDictionaries);
  
        // Try to initialize server (safe fail)
        try {
          await initializeServerDictionaries();
          console.log("Server dictionaries initialized");
        } catch (err) {
          console.warn("Could not initialize server dictionaries, running offline mode");
        }
  
        // Request permissions
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (status !== 'granted') {
          Alert.alert('Permission required', 'We need access to your photos to select images');
        }
  
        console.log("App initialization complete.");
      } catch (error) {
        console.error('Initialization error:', error);
        Alert.alert('Initialization Error', 'Failed to initialize app components');
      }
    };
    
    initializeApp();
  
    return () => {
      if (isAudioInitialized) {
        Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
          playsInSilentModeIOS: false,
          shouldDuckAndroid: false,
          staysActiveInBackground: false,
          playThroughEarpieceAndroid: false,
        });
      }
    };
  }, []);
  

  const handleAddToHistory = async (word: string, reading: string, definition: string) => {
    await addToHistory(word, reading, definition, history, setHistory);
  };

  const handleExportHistory = async () => {
    try {
      await exportHistoryService(history);
    } catch (error) {
      Alert.alert('Export Failed', error instanceof Error ? error.message : 'Unknown error occurred');
    }
  };

  const handleClearHistory = async () => {
    try {
      await clearHistoryService(setHistory);
      Alert.alert('Success', 'History cleared');
    } catch (error) {
      Alert.alert('Error', 'Failed to clear history');
    }
  };

  return {
    image,
    setImage,
    text,
    setText,
    words,
    setWords,
    currentWord,
    setCurrentWord,
    currentReading,
    setCurrentReading,
    definition,
    setDefinition,
    definitionImages,
    setDefinitionImages,
    loading,
    setLoading,
    error,
    setError,
    isVertical,
    setIsVertical,
    isDefinitionModalVisible,
    setIsDefinitionModalVisible,
    isSidebarVisible,
    setIsSidebarVisible,
    isDictionaryManagerVisible,
    setIsDictionaryManagerVisible,
    history,
    setHistory,
    dictionaries,
    setDictionaries,
    uploadProgress,
    setUploadProgress,
    decks,
    setDecks,
    currentDeckIndex,
    setCurrentDeckIndex,
    isReviewing,
    setIsReviewing,
    currentReviewCard,
    setCurrentReviewCard,
    showAnswer,
    setShowAnswer,
    isViewingDeck,
    setIsViewingDeck,
    viewingDeckIndex,
    setViewingDeckIndex,
    isFastMode,
    setIsFastMode,
    cropStart,
    setCropStart,
    cropEnd,
    setCropEnd,
    cropping,
    setCropping,
    currentMode,
    setCurrentMode,
    dictionaryWordList,
    setDictionaryWordList,
    isViewingDeckWords,
    setIsViewingDeckWords,
    newDeckName,
    setNewDeckName,
    isCreateDeckModalVisible,
    setIsCreateDeckModalVisible,
    isAudioInitialized,
    sidebarAnimation,
    handleAddToHistory,
    handleExportHistory,
    handleClearHistory,
    kanjiComponents,
    setKanjiComponents
  };
};
