// src/components/TopBar.tsx
import React from 'react';
import { TouchableOpacity, Text, View } from 'react-native';
import styles from '.././styles/styles';
import { Deck, DictionaryInfo } from '../models/types';

interface TopBarProps {
  toggleSidebar: () => void;
  decks: Deck[];
  dictionaries: DictionaryInfo[];
  userId?: string;
}

const TopBar: React.FC<TopBarProps> = ({
  toggleSidebar,
  decks,
  dictionaries,
  userId = "default_user"
}) => {
  return (
    <View style={styles.topBar}>
      <TouchableOpacity onPress={toggleSidebar} style={styles.sidebarToggle}>
        <Text style={styles.sidebarToggleText}>三</Text>
      </TouchableOpacity>
      <Text style={styles.title}>YomiScan</Text>
    </View>
  );
};

export default TopBar;