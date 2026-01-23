// src/services/textRenderer.ts
import React from 'react';
import { Text, TouchableOpacity } from 'react-native';
import { fetchDefinition } from './dictionaryService';
import styles from '../styles/styles';

export const renderTextWithClickableWords = (
  text: string,
  words: string[],
  fetchDefinition: (word: string) => void
): React.ReactNode => {
  if (!text || !words.length) return null;

  let currentIndex = 0;
  const wordElements = [];

  for (const word of words) {
    const startIndex = text.indexOf(word, currentIndex);
    if (startIndex === -1) continue;

    if (startIndex > currentIndex) {
      const nonWordText = text.slice(currentIndex, startIndex);
      wordElements.push(
        <Text key={`non-word-${currentIndex}`} style={styles.text}>
          {nonWordText}
        </Text>
      );
    }

    wordElements.push(
      <TouchableOpacity key={`word-${startIndex}`} onPress={() => fetchDefinition(word)}>
        <Text style={styles.wordText}>{word}</Text>
      </TouchableOpacity>
    );

    currentIndex = startIndex + word.length;
  }

  if (currentIndex < text.length) {
    const remainingText = text.slice(currentIndex);
    wordElements.push(
      <Text key="non-word-end" style={styles.text}>
        {remainingText}
      </Text>
    );
  }

  return wordElements;
};