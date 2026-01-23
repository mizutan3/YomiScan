// src/services/audioService.ts
import { Audio } from 'expo-av';
import axios from 'axios';
import { API_BASE_URL } from './api';

let sound: Audio.Sound | null = null;

export const initializeAudio = async () => {
  await Audio.setAudioModeAsync({
    allowsRecordingIOS: false,
    playsInSilentModeIOS: true,
    shouldDuckAndroid: true,
    staysActiveInBackground: false,
    playThroughEarpieceAndroid: false,
  });
};

export const playJapaneseAudio = async (text: string) => {
  try {
    // Stop any currently playing audio
    if (sound) {
      await sound.stopAsync();
      await sound.unloadAsync();
      sound = null;
    }

    // Get the audio data from the server
    const response = await axios.post(`${API_BASE_URL}/synthesize_speech`, { text });
    
    if (response.data.success) {
      const audioUri = `data:audio/mp3;base64,${response.data.audio}`;
      
      // Play the audio
      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: audioUri },
        { shouldPlay: true }
      );
      sound = newSound;
    }
  } catch (error) {
    console.error('Audio playback error:', error);
    throw error;
  }
};

export const stopAudio = async () => {
  if (sound) {
    await sound.stopAsync();
    await sound.unloadAsync();
    sound = null;
  }
};

export const cleanupAudio = async () => {
  await stopAudio();
  await Audio.setAudioModeAsync({
    allowsRecordingIOS: false,
    playsInSilentModeIOS: false,
    shouldDuckAndroid: false,
    staysActiveInBackground: false,
    playThroughEarpieceAndroid: false,
  });
};