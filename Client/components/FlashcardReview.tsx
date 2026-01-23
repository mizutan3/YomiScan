// src/components/FlashcardReview.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, Modal, ScrollView, TouchableOpacity } from 'react-native';
import styles from '../styles/styles';
import { Rating } from "ts-fsrs";
import { playJapaneseAudio, stopAudio } from '../services/audioService';

interface FlashcardReviewProps {
  visible: boolean;
  currentReviewCard: any;
  showAnswer: boolean;
  setShowAnswer: (show: boolean) => void;
  decks: any[];
  currentDeckIndex: number;
  handleRating: (rating: any) => void;
  setIsReviewing: (reviewing: boolean) => void;
}

const FlashcardReview: React.FC<FlashcardReviewProps> = ({
  visible,
  currentReviewCard,
  showAnswer,
  setShowAnswer,
  decks,
  currentDeckIndex,
  handleRating,
  setIsReviewing
}) => {
  useEffect(() => {
    // Clean up audio when component unmounts
    return () => {
      stopAudio();
    };
  }, []);

  const handlePlayAudio = async () => {
    try {
      if (currentReviewCard?.word) {
        await playJapaneseAudio(currentReviewCard.word);
      }
    } catch (error) {
      console.error('Failed to play audio:', error);
    }
  };

  return (
    <Modal visible={visible} animationType="slide" transparent={false}>
      <View style={styles.reviewContainer}>
        {currentReviewCard && (
          <>
            <View style={styles.reviewHeader}>
              <TouchableOpacity
                onPress={() => setIsReviewing(false)}
                style={styles.closeButton}
                activeOpacity={0.7}
              >
                <Text style={styles.closeButtonText}>✕</Text>
              </TouchableOpacity>
              <Text style={styles.reviewDeckName}>{decks[currentDeckIndex].name}</Text>
            </View>

            <View style={styles.reviewContent}>
              <Text style={styles.reviewWord}>{currentReviewCard.word}</Text>
              
              {!showAnswer && (
                <TouchableOpacity
                  onPress={() => setShowAnswer(true)}
                  style={styles.showAnswerButton}
                  activeOpacity={0.7}
                >
                  <Text style={styles.showAnswerButtonText}>Show Answer</Text>
                </TouchableOpacity>
              )}

              {showAnswer && (
                <>
                  <View style={styles.answerHeader}>
                    <Text style={styles.reviewReading}>{currentReviewCard.reading}</Text>
                    <TouchableOpacity
                      onPress={handlePlayAudio}
                      style={styles.playButton}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.playButtonText}>Play</Text>
                    </TouchableOpacity>
                  </View>

                  <ScrollView style={styles.reviewDefinitionContainer}>
                    <Text style={styles.reviewDefinition}>{currentReviewCard.definition}</Text>
                  </ScrollView>

                  <View style={styles.ratingButtons}>
                    <TouchableOpacity
                      onPress={() => handleRating(Rating.Again)}
                      style={[styles.ratingButton, styles.againButton]}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.ratingButtonText}>Again</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      onPress={() => handleRating(Rating.Hard)}
                      style={[styles.ratingButton, styles.hardButton]}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.ratingButtonText}>Hard</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      onPress={() => handleRating(Rating.Good)}
                      style={[styles.ratingButton, styles.goodButton]}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.ratingButtonText}>Good</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      onPress={() => handleRating(Rating.Easy)}
                      style={[styles.ratingButton, styles.easyButton]}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.ratingButtonText}>Easy</Text>
                    </TouchableOpacity>
                  </View>
                </>
              )}
            </View>
          </>
        )}
      </View>
    </Modal>
  );
};

export default FlashcardReview;