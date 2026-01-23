// src/components/Sidebar.tsx
import React from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  FlatList, 
  Switch,
  Animated 
} from 'react-native';
import styles from '../styles/styles';

interface SidebarProps {
  isSidebarVisible: boolean;
  sidebarAnimation: Animated.Value;
  closeSidebar: () => void;
  isVertical: boolean;
  setIsVertical: (value: boolean) => void;
  isFastMode: boolean;
  setIsFastMode: (value: boolean) => void;
  setIsDictionaryManagerVisible: (value: boolean) => void;
  exportHistory: () => void;
  clearHistory: () => void;
  history: any[];
  setCurrentWord: (word: string) => void;
  setCurrentReading: (reading: string) => void;
  setDefinition: (definition: string) => void;
  setIsDefinitionModalVisible: (visible: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isSidebarVisible,
  sidebarAnimation,
  closeSidebar,
  isVertical,
  setIsVertical,
  isFastMode,
  setIsFastMode,
  setIsDictionaryManagerVisible,
  exportHistory,
  clearHistory,
  history,
  setCurrentWord,
  setCurrentReading,
  setDefinition,
  setIsDefinitionModalVisible
}) => {
  return (
    <Animated.View style={[styles.sidebar, { transform: [{ translateX: sidebarAnimation }] }]}>
      <View style={styles.sidebarContent}>
        <View style={styles.sidebarHeader}>
          <Text style={styles.sidebarTitle}>Settings</Text>
          <TouchableOpacity onPress={closeSidebar} style={styles.closeSidebarButton}>
            <Text style={styles.closeSidebarButtonText}>✕</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.switchContainer}>
          <Text style={styles.switchLabel}>Vertical:</Text>
          <View style={styles.switchWrapper}>
            <Switch
              value={isVertical}
              onValueChange={setIsVertical}
              trackColor={{ false: "#000000", true: "#81b0ff" }}
              thumbColor={isVertical ? "#f5dd4b" : "#f4f3f4"}
            />
          </View>
          <Text style={[styles.switchLabel, {marginLeft: 20}]}>Fast:</Text>
          <View style={styles.switchWrapper}>
            <Switch
              value={isFastMode}
              onValueChange={setIsFastMode}
              trackColor={{ false: "#000000", true: "#81b0ff" }}
              thumbColor={isFastMode ? "#f5dd4b" : "#f4f3f4"}
            />
          </View>
        </View>
        <View style={styles.sidebarSection}>
          <Text style={styles.sidebarSubtitle}>Dictionaries</Text>
          <TouchableOpacity 
            onPress={() => {
              setIsDictionaryManagerVisible(true);
              closeSidebar();
            }}
            style={styles.sidebarButton}
          >
            <Text style={styles.sidebarButtonText}>Dictionary Manager</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.sidebarSection}>
          <Text style={styles.sidebarSubtitle}>History</Text>
          <TouchableOpacity onPress={exportHistory} style={styles.sidebarButton}>
            <Text style={styles.sidebarButtonText}>Export History</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={clearHistory} style={[styles.sidebarButton, styles.clearButton]}>
            <Text style={styles.sidebarButtonText}>Clear History</Text>
          </TouchableOpacity>
          
          <FlatList
            data={history}
            keyExtractor={(item, index) => `${item.word}-${item.rawTimestamp}-${index}`}
            renderItem={({item}) => (
              <TouchableOpacity 
                onPress={() => {
                  setCurrentWord(item.word);
                  setCurrentReading(item.reading);
                  setDefinition(item.definition);
                  setIsDefinitionModalVisible(true);
                  closeSidebar();
                }}
                style={styles.historyItem}
              >
                <View style={styles.historyItemContent}>
                  <Text 
                    style={styles.historyWord}
                    numberOfLines={1}
                    ellipsizeMode="tail"
                  >
                    {item.word}
                  </Text>
                  <Text 
                    style={styles.historyReading}
                    numberOfLines={1}
                    ellipsizeMode="tail"
                  >
                    {item.reading}
                  </Text>
                  <Text 
                    style={styles.historyTimestamp}
                    numberOfLines={1}
                    ellipsizeMode="tail"
                  >
                    {item.timestamp}
                  </Text>
                </View>
              </TouchableOpacity>
            )}
            style={styles.historyList}
          />
        </View>
      </View>
    </Animated.View>
  );
};

export default Sidebar;