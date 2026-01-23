// src/services/dictionaryService.ts
import axios from 'axios';
import { API_BASE_URL } from './api';
import { DictionaryInfo } from '../models/types';
import * as DocumentPicker from 'expo-document-picker';
import { Alert } from 'react-native';
import {getDeviceId} from './../services/syncService'

export const loadDictionaries = async (): Promise<DictionaryInfo[]> => {
  try {
    const deviceId = await getDeviceId(); 
    const response = await axios.get<DictionaryInfo[]>(`${API_BASE_URL}/dictionaries`, {
      params: { device_id: deviceId }
    });
    return [...response.data].sort((a, b) => a.position - b.position);
  } catch (error) {
    console.error("Error loading dictionaries:", error);
    throw new Error("Failed to load dictionary list");
  }
};

export const toggleDictionary = async (
  dictName: string, 
  shouldLoad: boolean,
  dictionaries: DictionaryInfo[],
  setDictionaries: (dictionaries: DictionaryInfo[]) => void
): Promise<void> => {
  try {
    setDictionaries(dictionaries.map(dict => {
      if (dict.name === dictName) {
        return { ...dict, loading: true, error: undefined };
      }
      return dict;
    }));

    const endpoint = shouldLoad ? "load" : "unload";
    const deviceId = await getDeviceId();
    const response = await axios.post(`${API_BASE_URL}/dictionaries/${endpoint}`, {
      name: dictName,
      device_id: deviceId
    });

    setDictionaries(dictionaries.map(dict => {
      if (dict.name === dictName) {
        return {
          ...dict,
          loading: false,
          loaded: response.data.success ? shouldLoad : dict.loaded,
          error: response.data.error || undefined
        };
      }
      return dict;
    }));

    if (response.data.error) {
      throw new Error(response.data.error);
    }
  } catch (error) {
    setDictionaries(dictionaries.map(dict => {
      if (dict.name === dictName) {
        return {
          ...dict,
          loading: false,
          error: "Failed to toggle dictionary"
        };
      }
      return dict;
    }));
    throw error;
  }
};

/*
export const uploadDictionary = async (
    setUploadProgress: (progress: number) => void,
    dictionaries: DictionaryInfo[],
    setDictionaries: (dictionaries: DictionaryInfo[]) => void
  ): Promise<void> => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/zip', 'application/x-zip-compressed'],
        copyToCacheDirectory: true,
      });
  
      if (!result.canceled && result.assets && result.assets.length > 0) {
        setUploadProgress(0);
        const file = result.assets[0];
        
        const formData = new FormData();
        formData.append('file', {
          uri: file.uri,
          name: file.name,
          type: file.mimeType || 'application/zip',
        } as any);
  
        const response = await axios.post(`${API_BASE_URL}/dictionaries/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(progress);
            }
          },
        });
  
        if (response.data.error) {
          throw new Error(response.data.error);
        }
  
        // Update the dictionaries list after successful upload
        const updatedDictionaries = await loadDictionaries();
        setDictionaries(updatedDictionaries);
  
        Alert.alert(
          "Success", 
          `Dictionary "${response.data.name}" uploaded successfully`
        );
      } else {
        throw new Error('No file selected');
      }
    } catch (error) {
      setUploadProgress(0);
      console.error("Upload error:", error);
      throw error;
    }
  };*/
  
  /*
  export const deleteDictionary = async (
    dictName: string,
    dictionaries: DictionaryInfo[],
    setDictionaries: (dictionaries: DictionaryInfo[]) => void
  ): Promise<void> => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/dictionaries/${dictName}`);
      if (response.data.error) {
        throw new Error(response.data.error);
      }
      // Remove the deleted dictionary from the local state
      setDictionaries(dictionaries.filter(d => d.name !== dictName));
    } catch (error) {
      console.error("Error deleting dictionary:", error);
      throw error;
    }
  };*/
  
  export const moveDictionary = async (
    dictName: string,
    direction: 'up' | 'down',
    dictionaries: DictionaryInfo[],
    setDictionaries: (dictionaries: DictionaryInfo[]) => void
  ): Promise<void> => {
    try {
      const device_id = await getDeviceId();
  
      const orderResponse = await axios.get(`${API_BASE_URL}/dictionaries/order`, {
        params: { device_id }
      });
  
      const currentOrder: string[] = orderResponse.data.order;
      const index = currentOrder.indexOf(dictName);
      if (index === -1) return;
  
      const newIndex = direction === 'up' ? index - 1 : index + 1;
      if (newIndex < 0 || newIndex >= currentOrder.length) return;
  
      // swap
      [currentOrder[index], currentOrder[newIndex]] = [currentOrder[newIndex], currentOrder[index]];
  
      const response = await axios.post(`${API_BASE_URL}/dictionaries/reorder`, {
        order: currentOrder,
        device_id
      });
  
      if (response.data.success) {
        const updated = await loadDictionaries();
        setDictionaries(updated);
      }
    } catch (error) {
      console.error('❌ moveDictionary error:', error);
    }
  };
  
  export const fetchDefinition = async (
    word: string,
    setCurrentWord: (word: string) => void,
    setCurrentReading: (reading: string) => void,
    setDefinition: (definition: string) => void,
    setDefinitionImages: (images: string[]) => void,
    setIsDefinitionModalVisible: (visible: boolean) => void,
    addToHistory: (word: string, reading: string, definition: string) => Promise<void>,
    setLoading: (loading: boolean) => void,
    setError: (error: string | null) => void
  ): Promise<void> => {
    setLoading(true);
    setError(null);
    setCurrentWord(word);
    setDefinition("");
    setDefinitionImages([]);

    const controller = new AbortController(); // контролер для таймауту
    const { signal } = controller;
    // Встановлення таймауту на 1 секунду (1000 мс)
    const timeoutId = setTimeout(() => {
      controller.abort(); // припиняє запит якщо час відповіді на запит словника більший ніж 1 секунда
    }, 1000);
    const startTime = Date.now();

    try {
      const deviceId = await getDeviceId();
  
      const response = await axios.get(`${API_BASE_URL}/dictionary`, {
        params: {
          word,
          device_id: deviceId
        }
        ,
        signal,               // передаємо AbortController.signal
        timeout: 2000         // додатковий timeout на axios-запит
      });

      // Коли отримали відповідь
      const elapsed = Date.now() - startTime;
      console.log(`[Dictionary] Response time for "${word}": ${elapsed} ms`);
  
      clearTimeout(timeoutId);
  
      if (Array.isArray(response.data)) {
        const readings = response.data.map(entry => entry.reading).filter(Boolean);
        const primaryReading = readings.length > 0 ? readings[0] : "";
        setCurrentReading(primaryReading);
  
        const fullDefinition = response.data
  .map((entry: any) => {
    const header = entry.reading ? `【${entry.reading}】\n` : "";
    return `${header}${entry.meanings.join("\n")}`;
  })
  .join("\n\n");
  
        setDefinition(fullDefinition);
        setDefinitionImages(response.data.flatMap((entry: any) => entry.images || []));
        setIsDefinitionModalVisible(true);
  
        await addToHistory(word, primaryReading, fullDefinition);
      } else {
        setDefinition("Definition not found.");
        setCurrentReading("");
      }
    } catch (error: any) {
      // Якщо запит був abort-нутий через controller.abort()
      if (error.name === 'CanceledError' || error.message.includes('canceled')) {
        console.warn(`[Dictionary] Request for "${word}" was aborted due to timeout`);
        setError("Request timed out. Please try again.");
      } else {
        console.error("Error fetching definition:", error);
        setError("Failed to fetch definition. Please try again.");
      }
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };
  
  export const searchDictionaryWords = async (
    query: string,
    setDictionaryWordList: (words: string[]) => void
  ): Promise<void> => {
    try {
      const deviceId = await getDeviceId();
  
      const response = await axios.get(`${API_BASE_URL}/dictionary/search`, {
        params: {
          query,
          device_id: deviceId,
        }
      });
  
      if (Array.isArray(response.data)) {
        setDictionaryWordList(response.data);
      } else {
        setDictionaryWordList([]);
      }
    } catch (error) {
      console.error("Error searching dictionary:", error);
      setDictionaryWordList([]);
    }
  };

  export const synthesizeSpeech = async (text: string): Promise<string> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/synthesize_speech`, { text });
      if (response.data.success) {
        return response.data.audio;
      }
      throw new Error('Failed to synthesize speech');
    } catch (error) {
      console.error('Speech synthesis error:', error);
      throw error;
    }
  };