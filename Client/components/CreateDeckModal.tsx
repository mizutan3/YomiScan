// src/components/CreateDeckModal.tsx
import React from 'react';
import { 
  View, 
  Text, 
  Modal, 
  Pressable, 
  TextInput,
  TouchableOpacity 
} from 'react-native';
import styles from '../styles/styles';

interface CreateDeckModalProps {
  visible: boolean;
  newDeckName: string;
  setNewDeckName: (name: string) => void;
  createNewDeck: () => void;
  setIsCreateDeckModalVisible: (visible: boolean) => void;
}

const CreateDeckModal: React.FC<CreateDeckModalProps> = ({
  visible,
  newDeckName,
  setNewDeckName,
  createNewDeck,
  setIsCreateDeckModalVisible
}) => {
  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Create New Deck</Text>
          <Pressable
            onPress={() => setIsCreateDeckModalVisible(false)}
            style={styles.closeButton}
          >
            <Text style={styles.closeButtonText}>✕</Text>
          </Pressable>
        </View>

        <View style={styles.modalContent}>
          <TextInput
            style={styles.modalInput}
            placeholder="Enter deck name"
            placeholderTextColor="#AAAAAA"
            value={newDeckName}
            onChangeText={setNewDeckName}
            autoFocus={true}
          />
          
          <TouchableOpacity 
            onPress={createNewDeck}
            style={styles.primaryButton}
            disabled={!newDeckName.trim()}
          >
            <Text style={styles.primaryButtonText}>Create Deck</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

export default CreateDeckModal;