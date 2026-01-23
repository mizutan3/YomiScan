// src/components/DictionaryDefinitionModal.tsx
import React, { useEffect } from 'react';
import { View, Text, Modal, Pressable, ScrollView, Image, TouchableOpacity } from 'react-native';
import styles from '../styles/styles';
import { API_BASE_URL } from "../services/api";
import { playJapaneseAudio, stopAudio } from '../services/audioService';

interface DictionaryDefinitionModalProps {
  visible: boolean;
  currentWord: string;
  currentReading: string;
  definition: string;
  definitionImages: string[];
  addCardToDeck: (deckIndex: number, word: string, reading: string, definition: string) => void;
  currentDeckIndex: number;
  setIsDefinitionModalVisible: (visible: boolean) => void;
  decks: any[];
}

const DictionaryDefinitionModal: React.FC<DictionaryDefinitionModalProps> = ({
  visible,
  currentWord,
  currentReading,
  definition,
  definitionImages,
  addCardToDeck,
  currentDeckIndex,
  setIsDefinitionModalVisible,
  decks
}) => {
  useEffect(() => {
    return () => {
      stopAudio();
    };
  }, []);

  const handlePlayAudio = async () => {
    try {
      await playJapaneseAudio(currentWord);
    } catch (error) {
      console.error('Failed to play audio:', error);
    }
  };

  const isWordInDeck = () => {
    if (currentDeckIndex < 0 || currentDeckIndex >= decks.length) return false;
    return decks[currentDeckIndex].cards.some(
      (card: any) => card.word === currentWord && card.reading === currentReading
    );
  };

  const handleAddToDeck = () => {
    if (!isWordInDeck()) {
      addCardToDeck(currentDeckIndex, currentWord, currentReading, definition);
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
    >
      <View style={styles.modalContainer}>
        <View style={styles.definitionHeader}>
          <View style={styles.definitionHeaderLeft}>
            <Text style={styles.modalTitle}>{currentWord}</Text>
            {currentReading && <Text style={styles.modalReading}>{currentReading}</Text>}
          </View>
          
          <View style={styles.definitionHeaderRight}>
            <TouchableOpacity
              onPress={handlePlayAudio}
              style={styles.playButton}
              activeOpacity={0.7}
            >
              <Text style={styles.playButtonText}>▶</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              onPress={handleAddToDeck}
              style={[styles.addToDeckButton, isWordInDeck() && styles.disabledButton]}
              disabled={isWordInDeck()}
              activeOpacity={0.7}
            >
              <Text style={styles.addToDeckButtonText}>
                {isWordInDeck() ? '✔' : '✚'}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              onPress={() => setIsDefinitionModalVisible(false)}
              style={styles.closeButton}
              activeOpacity={0.7}
            >
              <Text style={styles.closeButtonText}>✖</Text>
            </TouchableOpacity>
          </View>
        </View>

        <ScrollView
          style={styles.modalContent}
          contentContainerStyle={{ flexGrow: 1, paddingBottom: 50, justifyContent: 'center' }}
        >
          <Text style={styles.modalText}>{definition}</Text>
          <View style={styles.imageContainer}>
            {definitionImages.map((imgSrc, index) => (
              <Image key={index} source={{ uri: `${API_BASE_URL}/${imgSrc}` }} style={styles.definitionImage} />
            ))}
          </View>
        </ScrollView>
      </View>
    </Modal>
  );
};

export default DictionaryDefinitionModal;