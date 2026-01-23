// src/services/ocrService.ts
import axios from 'axios';
import * as FileSystem from 'expo-file-system';
import { API_BASE_URL } from './api';
import * as ImagePicker from 'expo-image-picker';

export const processImage = async (
  imageUri: string,
  isVertical: boolean,
  isFastMode: boolean,
  setText: (text: string) => void,
  setWords: (words: string[]) => void,
  setLoading: (loading: boolean) => void,
  setError: (error: string | null) => void
): Promise<void> => {
  setLoading(true);
  try {
    const base64 = await FileSystem.readAsStringAsync(imageUri, { // Читання файлу зображення
      encoding: FileSystem.EncodingType.Base64 // Конвертація зображення в рядок base64
    });
    
    const response = await axios.post(`${API_BASE_URL}/ocr`, { // Надсилання даних зображення на сервер
      image: base64, // base64 кодування зображення
      orientation: isVertical ? "vertical" : "horizontal", // Орієнтація тексту
      fast_mode: isFastMode // Режим обробки зображення
    });

    setText(response.data.text);
    setWords(response.data.words);
  } catch (error) {
    console.error("Error processing image:", error);
    setError("Failed to process image. Please try again.");
  } finally {
    setLoading(false);
  }
};

export const processCroppedImage = async (
  imageUri: string,
  left: number,
  top: number,
  width: number,
  height: number,
  isVertical: boolean,
  isFastMode: boolean,
  setText: (text: string) => void,
  setWords: (words: string[]) => void,
  setLoading: (loading: boolean) => void,
  setError: (error: string | null) => void
): Promise<void> => {
  if (!imageUri) return;
  
  setLoading(true);
  try {
    const base64 = await FileSystem.readAsStringAsync(imageUri, { 
      encoding: FileSystem.EncodingType.Base64 
    });
    
    const response = await axios.post(`${API_BASE_URL}/ocr`, {
      image: base64,
      orientation: isVertical ? "vertical" : "horizontal",
      fast_mode: isFastMode,
      crop: {
        left,
        top,
        width,
        height
      }
    });

    setText(response.data.text);
    setWords(response.data.words);
  } catch (error) {
    console.error("Error processing cropped image:", error);
    setError("Failed to process selected area. Please try again.");
  } finally {
    setLoading(false);
  }
};