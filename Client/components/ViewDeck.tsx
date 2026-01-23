// src/components/ViewDeck.tsx
import React from 'react';
import {View, Text, Modal, Pressable, FlatList, Alert, TouchableOpacity } from 'react-native';
import styles from '../styles/styles';
import { exportDeck } from '../services/deckService';

interface ViewDeckProps {
  visible: boolean;
  decks: any[];
  viewingDeckIndex: number;
  currentDeckIndex: number;
  setCurrentDeckIndex: (index: number) => void;
  deleteDeck: (deckIndex: number) => void;
  deleteCardFromDeck: (deckIndex: number, cardIndex: number) => void;
  setIsViewingDeck: (viewing: boolean) => void;
}

const ViewDeck: React.FC<ViewDeckProps> = ({
  visible,
  decks,
  viewingDeckIndex,
  currentDeckIndex,
  setCurrentDeckIndex,
  deleteDeck,
  deleteCardFromDeck,
  setIsViewingDeck
}) => {
  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
    >
      <View style={styles.modalContainer}>
      <View style={styles.modalHeader}>
        <View style={styles.definitionHeaderLeft}>
          <Text style={styles.modalTitle} numberOfLines={1} ellipsizeMode="tail">
            {decks[viewingDeckIndex]?.name || 'Deck'}
          </Text>
        </View>

        <View style={styles.definitionHeaderRight}>
          <TouchableOpacity
            onPress={() => {
              setCurrentDeckIndex(viewingDeckIndex);
              Alert.alert("Success", `"${decks[viewingDeckIndex].name}" is now the current deck`);
            }}
            style={styles.emojiIconButton}
          >
            <Text style={styles.emojiIconText}>⭐</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => exportDeck(decks[viewingDeckIndex])}
            style={styles.emojiIconButton}
          >
            <Text style={styles.emojiIconText}>📤</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => deleteDeck(viewingDeckIndex)}
            style={styles.emojiIconButton}
          >
            <Text style={styles.emojiIconText}>🗑️</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => setIsViewingDeck(false)}
            style={styles.emojiIconButton}
          >
            <Text style={styles.emojiIconText}>✖</Text>
          </TouchableOpacity>
        </View>
      </View>

        <FlatList
          data={decks[viewingDeckIndex]?.cards || []}
          keyExtractor={(item, index) => `${item.word}-${index}`}
          renderItem={({item, index}) => (
            <View style={styles.cardItemContainer}>
              <View style={styles.cardContent}>
                <View style={styles.cardTextContainer}>
                  <Text style={styles.cardWord}>{item.word}</Text>
                  {item.reading && <Text style={styles.cardReading}>{item.reading}</Text>}
                  <Text style={styles.cardDueDate}>
                    Due: {new Date(item.card.due).toLocaleDateString()} at {new Date(item.card.due).toLocaleTimeString()}
                  </Text>
                </View>
                <Pressable
                  onPress={() => deleteCardFromDeck(viewingDeckIndex, index)}
                  style={styles.emojiIconButton}
                >
                  <Text style={styles.emojiIconText}>Delete</Text>
                </Pressable>
              </View>
            </View>
          )}
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateText}>No cards in this deck</Text>
            </View>
          }
          contentContainerStyle={styles.listContentContainer}
        />
      </View>
    </Modal>
  );
};

export default ViewDeck;