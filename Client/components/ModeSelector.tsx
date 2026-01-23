// src/components/ModeSelector.tsx
import React from 'react';
import { View, TouchableOpacity, Text, Button } from 'react-native';
import styles from '../styles/styles';

interface ModeSelectorProps {
  currentMode: 'ocr' | 'dictionary' | 'srs';
  setCurrentMode: (mode: 'ocr' | 'dictionary' | 'srs') => void;
  pickImage: () => void;
  pickImageFromGallery: () => void;
  showCaptureButtons: boolean;
}

const ModeSelector: React.FC<ModeSelectorProps> = ({
  currentMode,
  setCurrentMode,
  pickImage,
  pickImageFromGallery,
  showCaptureButtons
}) => {
  return (
    <>
      <View style={styles.modeSelector}>
        <TouchableOpacity 
          style={[styles.modeButton, currentMode === 'ocr' && styles.activeMode]}
          onPress={() => setCurrentMode('ocr')}
        >
          <Text style={styles.modeButtonText}>OCR</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.modeButton, currentMode === 'dictionary' && styles.activeMode]}
          onPress={() => setCurrentMode('dictionary')}
        >
          <Text style={styles.modeButtonText}>Dictionary</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.modeButton, currentMode === 'srs' && styles.activeMode]}
          onPress={() => setCurrentMode('srs')}
        >
          <Text style={styles.modeButtonText}>SRS</Text>
        </TouchableOpacity>
      </View>

      {showCaptureButtons && (
        <View style={styles.buttonContainer}>
          <View style={styles.captureButton}>
            <Button title="Capture Image" onPress={pickImage} color="#BB86FC" />
          </View>
          <View style={styles.galleryButton}>
            <Button title="Load from Gallery" onPress={pickImageFromGallery} color="#3700B3" />
          </View>
        </View>
      )}
    </>
  );
};

export default ModeSelector;