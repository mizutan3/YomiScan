// src/services/fsrsService.ts
import { FSRS, generatorParameters, Card, Rating } from 'ts-fsrs';
import { Flashcard, Deck } from '../models/types';
import { saveDecks } from './deckService';
import { Alert } from 'react-native';

export const fsrs = new FSRS(generatorParameters());

export const handleRating = async (
  rating: Rating,
  currentReviewCard: Flashcard | null,
  currentDeckIndex: number,
  decks: Deck[],
  setDecks: (decks: Deck[]) => void,
  setCurrentReviewCard: (card: Flashcard | null) => void,
  setIsReviewing: (reviewing: boolean) => void,
  setShowAnswer: (show: boolean) => void
): Promise<void> => {
  if (!currentReviewCard) return;

  const now = new Date();
  const scheduling = fsrs.repeat(currentReviewCard.card, now);
  
  let scheduledCard: any;
  switch (rating) {
    case Rating.Again:
      scheduledCard = scheduling[Rating.Again];
      break;
    case Rating.Hard:
      scheduledCard = scheduling[Rating.Hard];
      break;
    case Rating.Good:
      scheduledCard = scheduling[Rating.Good];
      break;
    case Rating.Easy:
      scheduledCard = scheduling[Rating.Easy];
      break;
    default:
      return;
  }

  const { card } = scheduledCard;

  const updatedDecks = [...decks];
  const deck = updatedDecks[currentDeckIndex];
  const cardIndex = deck.cards.findIndex(c => 
    c.word === currentReviewCard.word && 
    c.reading === currentReviewCard.reading
  );

  if (cardIndex !== -1) {
    updatedDecks[currentDeckIndex].cards[cardIndex] = {
      ...currentReviewCard,
      card
    };
    
    setDecks(updatedDecks);
    // Save the updated decks to AsyncStorage
    await saveDecks(updatedDecks);
  }

  const nextCard = updatedDecks[currentDeckIndex].cards.find(c => 
    new Date(c.card.due) <= now && 
    (c.word !== currentReviewCard.word || c.reading !== currentReviewCard.reading)
  );

  if (nextCard) {
    setCurrentReviewCard(nextCard);
    setShowAnswer(false);
  } else {
    setIsReviewing(false);
    setCurrentReviewCard(null);
  }
};

export const startReview = (
  deckIndex: number,
  decks: Deck[],
  setCurrentReviewCard: (card: Flashcard | null) => void,
  setIsReviewing: (reviewing: boolean) => void,
  setShowAnswer: (show: boolean) => void,
  setCurrentDeckIndex: (index: number) => void
): void => {
  try {
      const deck = decks[deckIndex];
      if (!deck || !deck.cards || deck.cards.length === 0) {
          Alert.alert("No Cards", "This deck has no cards to review");
          return;
      }

      // Find the first card that's due for review
      const now = new Date();
      const dueCard = deck.cards.find(card => new Date(card.card.due) <= now);
      
      if (dueCard) {
          setCurrentReviewCard(dueCard);
          setIsReviewing(true);
          setShowAnswer(false);
          setCurrentDeckIndex(deckIndex);
      } else {
          Alert.alert(
              "No Cards Due", 
              "All cards in this deck are scheduled for later review"
          );
      }
  } catch (error) {
      console.error("Error starting review:", error);
      Alert.alert("Error", "Failed to start review session");
  }
};