// src/App.tsx
import React from 'react';
import { StatusBar } from "expo-status-bar";
import { View, StyleSheet, Dimensions } from "react-native";
import { useAppState } from './hooks/useAppState';
import TopBar from './components/TopBar';
import Sidebar from './components/Sidebar';
import OCRScanner from './components/OCRScanner';
import DictionarySearch from './components/DictionarySearch';
import SRSView from './components/SRSView';
import ModeSelector from './components/ModeSelector';
import DictionaryDefinitionModal from './components/DictionaryDefinitionModal';
import FlashcardReview from './components/FlashcardReview';
import DictionaryManager from './components/DictionaryManager';
import ViewDeck from './components/ViewDeck';
import CreateDeckModal from './components/CreateDeckModal';
import { fetchDefinition, searchDictionaryWords, toggleDictionary, moveDictionary,} from './services/dictionaryService';
import { pickImage, pickImageFromGallery,} from './services/imagePickerService';
import { handleImageTouchStart, handleImageTouchMove, handleImageTouchEnd } from './services/touchHandlers';
import { toggleSidebar, closeSidebar } from './services/sidebarAnimations';
import { renderTextWithClickableWords } from './services/textRenderer';
import { addCardToDeck,deleteCardFromDeck,deleteDeck,createNewDeck,} from './services/deckService';
import { handleRating, startReview } from './services/fsrsService';
import { uploadDictionaryState } from './services/syncService';


const { width: screenWidth, height: screenHeight } = Dimensions.get("window");

export default function App() {
  const state = useAppState();
  
  return (
    <View style={styles.container}>
      <StatusBar style="light" />

      <TopBar
        toggleSidebar={() => toggleSidebar(
          state.isSidebarVisible,
          state.setIsSidebarVisible,
          state.sidebarAnimation
        )}
        decks={state.decks}
        dictionaries={state.dictionaries}
        userId="default_user"
      />

      <Sidebar
        isSidebarVisible={state.isSidebarVisible}
        sidebarAnimation={state.sidebarAnimation}
        closeSidebar={() => closeSidebar(state.setIsSidebarVisible, state.sidebarAnimation)}
        isVertical={state.isVertical}
        setIsVertical={state.setIsVertical}
        isFastMode={state.isFastMode}
        setIsFastMode={state.setIsFastMode}
        setIsDictionaryManagerVisible={state.setIsDictionaryManagerVisible}
        exportHistory={state.handleExportHistory}
        clearHistory={state.handleClearHistory}
        history={state.history}
        setCurrentWord={state.setCurrentWord}
        setCurrentReading={state.setCurrentReading}
        setDefinition={state.setDefinition}
        setIsDefinitionModalVisible={state.setIsDefinitionModalVisible}
      />

      <View style={[styles.mainContent, state.isSidebarVisible && styles.disabledMainContent]}>
        {state.currentMode === 'ocr' && (
          <OCRScanner
            image={state.image}
            loading={state.loading}
            error={state.error}
            text={state.text}
            words={state.words}
            cropStart={state.cropStart}
            cropEnd={state.cropEnd}
            cropping={state.cropping}
            handleImageTouchStart={(e) => handleImageTouchStart(
              e,
              state.image,
              state.setCropStart,
              state.setCropEnd,
              state.setCropping
            )}
            handleImageTouchMove={(e) => handleImageTouchMove(
              e,
              state.cropping,
              state.image,
              state.setCropEnd
            )}
            handleImageTouchEnd={() => handleImageTouchEnd(
              state.cropping,
              state.image,
              state.cropStart,
              state.cropEnd,
              state.setCropping,
              state.setCropStart,
              state.setCropEnd,
              state.isVertical,
              state.isFastMode,
              state.setText,
              state.setWords,
              state.setLoading,
              state.setError
            )}
            renderTextWithClickableWords={() => renderTextWithClickableWords(
              state.text,
              state.words,
              (word) => fetchDefinition(
                word,
                state.setCurrentWord,
                state.setCurrentReading,
                state.setDefinition,
                state.setDefinitionImages,
                state.setIsDefinitionModalVisible,
                state.handleAddToHistory,
                state.setLoading,
                state.setError
              )
            )}
            pickImage={() => pickImage(state.setImage, state.setLoading, state.setError)}
            pickImageFromGallery={() => pickImageFromGallery(state.setImage, state.setLoading, state.setError)}
          />
        )}

        {state.currentMode === 'dictionary' && (
          <DictionarySearch
            currentWord={state.currentWord}
            setCurrentWord={state.setCurrentWord}
            fetchDefinition={(word) => fetchDefinition(
              word,
              state.setCurrentWord,
              state.setCurrentReading,
              state.setDefinition,
              state.setDefinitionImages,
              state.setIsDefinitionModalVisible,
              state.handleAddToHistory,
              state.setLoading,
              state.setError
            )}
            dictionaryWordList={state.dictionaryWordList}
            searchDictionaryWords={(query) => searchDictionaryWords(
              query,
              state.setDictionaryWordList
            )}
            setDictionaryWordList={state.setDictionaryWordList}
          />
        )}

        {state.currentMode === 'srs' && (
          <SRSView
            isViewingDeckWords={state.isViewingDeckWords}
            setIsViewingDeckWords={state.setIsViewingDeckWords}
            decks={state.decks}
            currentDeckIndex={state.currentDeckIndex}
            startReview={(deckIndex) => startReview(
              deckIndex,
              state.decks,
              state.setCurrentReviewCard,
              state.setIsReviewing,
              state.setShowAnswer,
              state.setCurrentDeckIndex
            )}
            setViewingDeckIndex={state.setViewingDeckIndex}
            setIsViewingDeck={state.setIsViewingDeck}
            setIsCreateDeckModalVisible={state.setIsCreateDeckModalVisible}
            setCurrentWord={state.setCurrentWord}
            setCurrentReading={state.setCurrentReading}
            setDefinition={state.setDefinition}
            setIsDefinitionModalVisible={state.setIsDefinitionModalVisible}
          />
        )}

        <ModeSelector
          currentMode={state.currentMode}
          setCurrentMode={state.setCurrentMode}
          pickImage={() => pickImage(state.setImage, state.setLoading, state.setError)}
          pickImageFromGallery={() => pickImageFromGallery(state.setImage, state.setLoading, state.setError)}
          showCaptureButtons={state.currentMode === 'ocr'}
        />
      </View>

      <DictionaryDefinitionModal
        visible={state.isDefinitionModalVisible}
        currentWord={state.currentWord}
        currentReading={state.currentReading}
        definition={state.definition}
        definitionImages={state.definitionImages}
        addCardToDeck={(deckIndex, word, reading, definition) => addCardToDeck(
          deckIndex,
          word,
          reading,
          definition,
          state.decks,
          state.setDecks
        )}
        currentDeckIndex={state.currentDeckIndex}
        setIsDefinitionModalVisible={state.setIsDefinitionModalVisible}
        decks={state.decks} // Add this line
      />

      <CreateDeckModal
        visible={state.isCreateDeckModalVisible}
        newDeckName={state.newDeckName}
        setNewDeckName={state.setNewDeckName}
        createNewDeck={() => createNewDeck(
          state.newDeckName,
          state.decks,
          state.setDecks,
          state.setNewDeckName,
          state.setIsCreateDeckModalVisible
        )}
        setIsCreateDeckModalVisible={state.setIsCreateDeckModalVisible}
      />

        <DictionaryManager
          visible={state.isDictionaryManagerVisible}
          dictionaries={state.dictionaries}
          //uploadProgress={state.uploadProgress}
          toggleDictionary={(dictName, shouldLoad) => toggleDictionary(
            dictName,
            shouldLoad,
            state.dictionaries,
            state.setDictionaries
          )}
          /*deleteDictionary={(dictName) => deleteDictionary(
            dictName,
            state.dictionaries,
            state.setDictionaries
          )}*/
          moveDictionary={(dictName, direction) => moveDictionary(
            dictName,
            direction,
            state.dictionaries,
            state.setDictionaries
          )}
          setIsDictionaryManagerVisible={state.setIsDictionaryManagerVisible}
          onSync={async () => {
            const active = state.dictionaries.filter(d => d.loaded).map(d => d.name);
            const order = state.dictionaries.map(d => d.name);
            await uploadDictionaryState(active, order);
          }}
        />

      <FlashcardReview
        visible={state.isReviewing}
        currentReviewCard={state.currentReviewCard}
        showAnswer={state.showAnswer}
        setShowAnswer={state.setShowAnswer}
        decks={state.decks}
        currentDeckIndex={state.currentDeckIndex}
        handleRating={(rating) => handleRating(
          rating,
          state.currentReviewCard,
          state.currentDeckIndex,
          state.decks,
          state.setDecks,
          state.setCurrentReviewCard,
          state.setIsReviewing,
          state.setShowAnswer
        )}
        setIsReviewing={state.setIsReviewing}
      />

      <ViewDeck
        visible={state.isViewingDeck}
        decks={state.decks}
        viewingDeckIndex={state.viewingDeckIndex}
        currentDeckIndex={state.currentDeckIndex}
        setCurrentDeckIndex={state.setCurrentDeckIndex}
        deleteDeck={(deckIndex) => deleteDeck(
          deckIndex,
          state.decks,
          state.currentDeckIndex,
          state.setDecks,
          state.setCurrentDeckIndex,
          state.setIsViewingDeck
        )}
        deleteCardFromDeck={(deckIndex, cardIndex) => deleteCardFromDeck(
          deckIndex,
          cardIndex,
          state.decks,
          state.setDecks
        )}
        setIsViewingDeck={state.setIsViewingDeck}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#ffffff",
  },
  mainContent: {
    flex: 1,
    justifyContent: "flex-start",
    paddingHorizontal: 20,
    paddingTop: 0,
  },
  disabledMainContent: {
    opacity: 0.5,
  }
});
