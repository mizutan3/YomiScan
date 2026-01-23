// src/components/SRSView.tsx
import React from 'react';
import { 
  View, 
  TouchableOpacity, 
  Text, 
  FlatList 
} from 'react-native';
import styles from '../styles/styles';
import { Flashcard } from '../models/types';

interface SRSViewProps {
    isViewingDeckWords: boolean;
    setIsViewingDeckWords: (value: boolean) => void;
    decks: {
      name: string;
      cards: Flashcard[];
    }[];
    currentDeckIndex: number;
    startReview: (deckIndex: number) => void;
    setViewingDeckIndex: (index: number) => void;
    setIsViewingDeck: (value: boolean) => void;
    setIsCreateDeckModalVisible: (value: boolean) => void;
    setCurrentWord: (word: string) => void;
    setCurrentReading: (reading: string) => void;
    setDefinition: (definition: string) => void;
    setIsDefinitionModalVisible: (visible: boolean) => void;
  }
  
  const SRSView: React.FC<SRSViewProps> = ({
    isViewingDeckWords,
    setIsViewingDeckWords,
    decks,
    currentDeckIndex,
    startReview,
    setViewingDeckIndex,
    setIsViewingDeck,
    setIsCreateDeckModalVisible,
    setCurrentWord,
    setCurrentReading,
    setDefinition,
    setIsDefinitionModalVisible
  }) => {
  return (
    <View style={styles.srsContainer}>
      {!isViewingDeckWords ? (
        <>
          <View style={styles.deckActions}>
            <TouchableOpacity 
              onPress={() => setIsViewingDeckWords(true)}
              style={[styles.deckSRSButton, {flex: 1, marginRight: 5}]}
            >
              <Text style={styles.deckSRSButtonText}>Browse</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              onPress={() => setIsCreateDeckModalVisible(true)}
              style={[styles.deckSRSButton, {flex: 1, marginLeft: 5}]}
            >
              <Text style={styles.deckSRSButtonText}>Create Deck</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            data={decks}
            keyExtractor={(item, index) => `${item.name}-${index}`}
            renderItem={({item, index}) => (
              <TouchableOpacity 
                style={[
                  styles.deckItem,
                  currentDeckIndex === index && styles.currentDeckItem
                ]}
                onPress={() => {
                  startReview(index);
                }}
                onLongPress={() => {
                  setViewingDeckIndex(index);
                  setIsViewingDeck(true);
                }}
              >
                <Text style={styles.deckName}>{item.name}</Text>
                <View style={styles.deckStats}>
                  <Text style={styles.deckCount}>
                    {item.cards.length} cards
                  </Text>
                  <Text style={styles.dueCount}>
                    {item.cards.filter(card => new Date(card.card.due) <= new Date()).length} due
                  </Text>
                </View>
                {currentDeckIndex === index && (
                  <Text style={styles.currentDeckIndicator}>Current</Text>
                )}
              </TouchableOpacity>
            )}
            style={styles.deckList}
          />
        </>
      ) : (
        <>
          <TouchableOpacity 
            onPress={() => setIsViewingDeckWords(false)}
            style={styles.backButton}
          >
            <Text style={styles.backButtonText}>← Back to Decks</Text>
          </TouchableOpacity>
          <FlatList
            data={decks.flatMap(deck => 
              deck.cards.map(card => ({ ...card, deckName: deck.name }))
            )}
            keyExtractor={(item, index) => `${item.word}-${index}`}
            renderItem={({item}) => (
              <TouchableOpacity 
                style={styles.wordItem}
                onPress={() => {
                  setCurrentWord(item.word);
                  setCurrentReading(item.reading);
                  setDefinition(item.definition);
                  setIsDefinitionModalVisible(true);
                }}
              >
                <View style={styles.wordItemHeader}>
                  <Text style={styles.wordItemText}>{item.word}</Text>
                  <Text style={styles.wordItemDeckName}>{item.deckName}</Text>
                </View>
                <Text style={styles.wordItemReading}>{item.reading}</Text>
              </TouchableOpacity>
            )}
            style={styles.wordList}
          />
        </>
      )}
    </View>
  );
};

export default SRSView;