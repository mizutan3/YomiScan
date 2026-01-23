// src/components/DictionarySearch.tsx
import React from 'react';
import { 
  View, 
  TextInput, 
  TouchableOpacity, 
  Text, 
  FlatList 
} from 'react-native';
import styles from '../styles/styles';

interface DictionarySearchProps {
    currentWord: string;
    setCurrentWord: (word: string) => void;
    fetchDefinition: (word: string) => void;
    dictionaryWordList: string[];
    searchDictionaryWords: (query: string) => void;
    setDictionaryWordList: (words: string[]) => void; // Add this line
  }

const DictionarySearch: React.FC<DictionarySearchProps> = ({
  currentWord,
  setCurrentWord,
  fetchDefinition,
  dictionaryWordList,
  searchDictionaryWords,
  setDictionaryWordList,
}) => {
  return (
    <View style={styles.dictionarySearchContainer}>
      <TextInput
        style={styles.dictionaryInput}
        placeholder="Enter word to search"
        placeholderTextColor="#2E2E2E"
        value={currentWord}
        onChangeText={(text) => {
          setCurrentWord(text);
          if (text.length > 0) {
            searchDictionaryWords(text);
          } else {
            setDictionaryWordList([]);
          }
        }}
        onSubmitEditing={() => fetchDefinition(currentWord)}
      />
      <TouchableOpacity 
        style={styles.searchButton}
        onPress={() => fetchDefinition(currentWord)}
      >
        <Text style={styles.searchButtonText}>Search</Text>
      </TouchableOpacity>
      
      {dictionaryWordList.length > 0 && (
        <View style={styles.wordListContainer}>
          <FlatList
            data={dictionaryWordList}
            keyExtractor={(item, index) => `${item}-${index}`}
            renderItem={({item}) => (
              <TouchableOpacity 
                style={styles.wordListItem}
                onPress={() => {
                  setCurrentWord(item);
                  fetchDefinition(item);
                }}
              >
                <Text style={styles.wordListText}>{item}</Text>
              </TouchableOpacity>
            )}
            style={styles.wordList}
            keyboardShouldPersistTaps="handled"
          />
        </View>
      )}
    </View>
  );
};

export default DictionarySearch;
