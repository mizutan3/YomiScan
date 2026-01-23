// src/components/DictionaryManager.tsx
import React from 'react';
import { 
  View, 
  Text, 
  Modal, 
  Pressable, 
  ScrollView, 
  TouchableOpacity, 
  Switch, 
  ActivityIndicator,
  Alert
} from 'react-native';
import styles from '../styles/styles';

interface DictionaryManagerProps {
    visible: boolean;
    dictionaries: any[];
    //uploadProgress: number;
    toggleDictionary: (dictName: string, shouldLoad: boolean) => void;
    //deleteDictionary: (dictName: string) => void;
    moveDictionary: (dictName: string, direction: 'up' | 'down') => void;
    setIsDictionaryManagerVisible: (visible: boolean) => void;
    onSync: () => Promise<void>;
}

const DictionaryManager: React.FC<DictionaryManagerProps> = ({
  visible,
  dictionaries,
  //uploadProgress,
  toggleDictionary,
  //deleteDictionary,
  moveDictionary,
  setIsDictionaryManagerVisible,
  onSync
}) => {
  const handleSync = async () => {
    try {
      await onSync();
      Alert.alert("Sync", "Dictionaries synced successfully!");
    } catch (e: any) {
      console.error(e);
      Alert.alert("Error", e.message || "Failed to sync.");
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Dictionary Manager</Text>
          <View style={styles.modalHeaderButtons}>
            <TouchableOpacity onPress={handleSync} style={styles.emojiIconButton}>
              <Text style={styles.emojiIconText}>⟳</Text>
            </TouchableOpacity>
            <Pressable
              onPress={() => setIsDictionaryManagerVisible(false)}
              style={styles.emojiIconButton}>
              <Text style={styles.emojiIconText}>✖</Text>
            </Pressable>
          </View>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Available Dictionaries</Text>
            
            {dictionaries.length === 0 ? (
              <Text style={styles.noDictionariesText}>No dictionaries available</Text>
            ) : (
              dictionaries.map((dict, index) => (
                <View key={dict.name} style={styles.dictionaryItem}>
                  <View style={styles.dictionaryInfo}>
                    <Text style={styles.dictionaryName}>{dict.name}</Text>
                    <View style={styles.statusContainer}>
                      {dict.loading ? (
                        <ActivityIndicator size="small" color="#BB86FC" />
                      ) : (
                        <Text style={dict.loaded ? styles.dictionaryStatusLoaded : styles.dictionaryStatusUnloaded}>
                          {dict.loaded ? "Loaded" : "Not Loaded"}
                        </Text>
                      )}
                    </View>
                    {dict.error && (
                      <Text style={styles.dictionaryError}>{dict.error}</Text>
                    )}
                  </View>
                  
                  <View style={styles.dictionaryActions}>
                    <View style={styles.moveButtons}>
                      <TouchableOpacity 
                        onPress={() => moveDictionary(dict.name, 'up')}
                        disabled={index === 0 || dict.loading}
                        style={[
                          styles.moveButton,
                          (index === 0 || dict.loading) && styles.disabledButton
                        ]}
                      >
                        <Text style={styles.moveButtonText}>↑</Text>
                      </TouchableOpacity>
                      <TouchableOpacity 
                        onPress={() => moveDictionary(dict.name, 'down')}
                        disabled={index === dictionaries.length - 1 || dict.loading}
                        style={[
                          styles.moveButton,
                          (index === dictionaries.length - 1 || dict.loading) && styles.disabledButton
                        ]}
                      >
                        <Text style={styles.moveButtonText}>↓</Text>
                      </TouchableOpacity>
                    </View>
                    
                    <Switch
                      value={dict.loaded}
                      onValueChange={(value) => toggleDictionary(dict.name, value)}
                      disabled={dict.loading}
                      trackColor={{ false: "#767577", true: "#81b0ff" }}
                      thumbColor={dict.loaded ? "#f5dd4b" : "#f4f3f4"}
                    />
                    {/*<TouchableOpacity 
                      onPress={() => deleteDictionary(dict.name)}
                      style={styles.deleteButton}
                      disabled={dict.loading}
                    >
                      <Text style={styles.deleteButtonText}>Delete</Text>
                      </TouchableOpacity>*/}
                  </View>
                </View>
              ))
            )}
          </View>

          {/*<View style={styles.section}>
            <Text style={styles.sectionTitle}>Upload New Dictionary</Text>
            <TouchableOpacity 
              onPress={uploadDictionary}
              style={styles.uploadButton}
            >
              <Text style={styles.uploadButtonText}>Select Dictionary File</Text>
            </TouchableOpacity>
            
            {uploadProgress > 0 && uploadProgress < 100 && (
              <View style={styles.progressContainer}>
                <Text style={styles.progressText}>Uploading: {uploadProgress}%</Text>
                <View style={styles.progressBar}>
                  <View 
                    style={[
                      styles.progressFill,
                      { width: `${uploadProgress}%` }
                    ]} 
                  />
                </View>
              </View>
            )}
          </View>*/}
        </ScrollView>
      </View>
    </Modal>
  );
};

export default DictionaryManager;