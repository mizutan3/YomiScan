// src/styles/styles.ts
import {StyleSheet, Dimensions} from "react-native";
const { width: screenWidth, height: screenHeight } = Dimensions.get("window");


const styles = StyleSheet.create({
    // Layout
    container: {
      flex: 1,
      backgroundColor: "#FFFFFF",
    },
    mainContent: {
      flex: 1,
      justifyContent: "flex-start",
      paddingHorizontal: 20,
      paddingTop: 0,
    },
  
    // Header
    topBar: {
      flexDirection: "row",
      alignItems: "center",
      padding: 10,
      height: 70,
      backgroundColor: "#f7f7f7",
      borderBottomWidth: 1,
      borderBottomColor: "#3700B3",
      marginBottom: 5
    },
    title: {
      fontSize: 24,
      paddingTop: 8,
      fontWeight: "bold",
      color: "#BB86FC",
      marginLeft: 20,
    },
    sidebarToggle: {
      padding: 10,
    },
    sidebarToggleText: {
      fontSize: 24,
      color: "#BB86FC",
    },
    modalHeaderContent: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    modalHeaderButtons: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 10,
    },
    headerActions: {
      flexDirection: 'row',
      alignItems: 'center',
    },
  
    // Sidebar
    sidebar: {
      position: "absolute",
      top: 0,
      left: 0,
      width: 300,
      height: "100%",
      backgroundColor: "#efefef",
      padding: 20,
      zIndex: 100, // Higher than other elements
    },
    sidebarContent: {
      flex: 1,
    },
    sidebarHeader: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: 20,
    },
    sidebarTitle: {
      fontSize: 26,
      fontWeight: "bold",
      color: "#BB86FC",
      marginBottom: 0,
    },
    closeSidebarButton: {
      padding: 10,
    },
    closeSidebarButtonText: {
      fontSize: 24,
      color: "#BB86FC",
    },
    sidebarSection: {
      marginTop: 20,
      borderTopWidth: 1,
      borderTopColor: '#3700B3',
      paddingTop: 20,
    },
    sidebarSubtitle: {
      fontSize: 18,
      fontWeight: 'bold',
      color: '#BB86FC',
      marginBottom: 10,
    },
    sidebarButton: {
      backgroundColor: '#3700B3',
      padding: 10,
      borderRadius: 5,
      marginBottom: 10,
    },
    clearButton: {
      backgroundColor: '#FF4444',
    },
    sidebarButtonText: {
      color: '#FFFFFF',
      textAlign: 'center',
    },
  
    // Image Processing
    imageContainer: {
      width: screenWidth * 0.9,
      height: screenHeight * 0.4,
      position: 'relative',
      overflow: 'hidden',
    },
    image: {
      width: '100%',
      height: '100%',
      resizeMode: "contain",
      borderRadius: 10,
      borderColor: "#3700B3",
      borderWidth: 1,
    },
    cropRectangle: {
      position: 'absolute',
      borderWidth: 2,
      borderColor: '#BB86FC',
      backgroundColor: 'rgba(187, 134, 252, 0.2)',
    },
    textContainer: {
      flex: 1,
      width: "100%",
      backgroundColor: "#ededed",
      borderRadius: 10,
      padding: 10,
      marginBottom: 0,
      borderWidth: 1,
      borderColor: "#3700B3",
      maxHeight: screenHeight * 0.33,
    },
    wordText: {
      color: "#BB86FC",
      fontSize: 16,
    },
    text: {
      fontSize: 16,
      color: "#FFFFFF",
      flexWrap: "wrap",
      lineHeight: 24,
      paddingVertical: 10,
    },
    heading: {
      fontSize: 18,
      fontWeight: "bold",
      marginTop: 10,
      marginBottom: 5,
      color: "#2e2e2e",
    },
  
    // Dictionary
    dictionarySearchContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 20,
    },
    dictionaryInput: {
      flex: 1,
      backgroundColor: '#FFFFFF',
      color: '#1e1e1e',
      padding: 12,
      borderRadius: 5,
      borderWidth: 1,
      borderColor: '#3700B3',
      marginRight: 10,
    },
    searchButton: {
      backgroundColor: '#3700B3',
      padding: 12,
      borderRadius: 5,
    },
    searchButtonText: {
      color: '#ffffff',
      fontWeight: 'bold',
    },
  
    // Modals
    modalContainer: {
      flex: 1,
      backgroundColor: "#FFFFFF",
    },
    modalHeader: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      padding: 20,
      borderBottomWidth: 1,
      borderBottomColor: "#3700B3",
    },
    definitionHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 15,
      borderBottomWidth: 1,
      borderBottomColor: '#3700B3',
    },
    definitionHeaderLeft: {
      flex: 1,
    },
    definitionHeaderRight: {
      flexDirection: 'row',
      alignItems: 'center',
      flexShrink: 0,
    },
    modalTitle: {
      fontSize: 20,
      fontWeight: 'bold',
      color: '#BB86FC',
      textAlign: 'left',
      flexShrink: 1
    },
    modalContent: {
      flex: 1,
      padding: 20,
    },
    listContentContainer: {
      padding: 16,
      flexGrow: 1,
    },
    definitionImage: {
      width: 300,
      height: 100,
      margin: 5,
      borderRadius: 5,
      borderWidth: 1,
      borderColor: "#BB86FC",
    },
    addToDeckButton: {
      backgroundColor: '#BB86FC',
      padding: 8,
      borderRadius: 5,
      marginTop: 2,
      marginRight: 0,
    },
    addToDeckButtonText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 14,
      textAlign: 'center',
    },
  
    // Review System
    reviewContainer: {
      flex: 1,
      backgroundColor: '#FFFFFF',
    },
    reviewHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 20,
      borderBottomWidth: 1,
      borderBottomColor: '#3700B3',
    },
    reviewDeckName: {
      fontSize: 18,
      color: '#BB86FC',
      marginLeft: 20,
    },
    reviewContent: {
      flex: 1,
      padding: 20,
    },
    reviewWord: {
      fontSize: 32,
      color: '#2D2D2D',
      textAlign: 'center',
      marginBottom: 30,
    },
    reviewReading: {
      fontSize: 20,
      color: '#BB86FC',
      textAlign: 'center',
      marginBottom: 20,
    },
    showAnswerButton: {
      backgroundColor: '#3700B3',
      padding: 15,
      borderRadius: 5,
      alignSelf: 'center',
    },
    showAnswerButtonText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 16,
    },
    ratingButtons: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginTop: 20,
    },
    ratingButton: {
      padding: 15,
      borderRadius: 5,
      flex: 1,
      marginHorizontal: 5,
      alignItems: 'center',
    },
    ratingButtonText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
    },
    againButton: {
      backgroundColor: '#F44336',
    },
    hardButton: {
      backgroundColor: '#FF9800',
    },
    goodButton: {
      backgroundColor: '#4CAF50',
    },
    easyButton: {
      backgroundColor: '#2196F3',
    },
  
    // Deck Management
    deckList: {
      flex: 1,
      padding: 15,
    },
    cardItem: {
      padding: 15,
      backgroundColor: '#1E1E1E',
      borderRadius: 8,
      marginBottom: 10,
      borderWidth: 1,
      borderColor: '#2D2D2D',
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    cardDefinition: {
      color: '#FFFFFF',
      fontSize: 14,
      marginTop: 8,
    },
    deleteCardButton: {
      backgroundColor: '#F44336',
      padding: 8,
      borderRadius: 5,
      marginLeft: 10,
    },
    deleteCardButtonText: {
      color: '#FFFFFF',
      fontSize: 12,
      fontWeight: 'bold',
    },
    noCardsText: {
      color: '#AAAAAA',
      textAlign: 'center',
      marginTop: 20,
      fontStyle: 'italic',
    },
  
    // Dictionary Manager
    dictionaryItem: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 12,
      backgroundColor: '#ededed',
      borderRadius: 8,
      marginBottom: 10,
      borderWidth: 1,
      borderColor: '#2D2D2D',
    },
    dictionaryInfo: {
      flex: 1,
      marginRight: 10,
    },
    dictionaryName: {
      color: '#2d2d2d',
      fontSize: 16,
      fontWeight: '500',
    },
    dictionaryStatusLoaded: {
      color: '#4CAF50',
      fontSize: 12,
    },
    dictionaryStatusUnloaded: {
      color: '#F44336',
      fontSize: 12,
    },
    dictionaryActions: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    emojiIconButton: {
      padding: 6,
      marginLeft: 8,
      borderRadius: 6,
      backgroundColor: '#ededed',
      alignItems: 'center',
      justifyContent: 'center',

    },
    emojiIconText: {
      fontWeight: 'bold',
      fontSize: 20,
      color: '#BB86FC',
    },

    uploadButton: {
      backgroundColor: '#3700B3',
      padding: 15,
      borderRadius: 5,
      alignItems: 'center',
      marginTop: 10,
    },
    uploadButtonText: {
      color: '#FFFFFF',
      fontSize: 16,
    },
    progressContainer: {
      marginTop: 10,
    },
    progressText: {
      color: '#FFFFFF',
      fontSize: 14,
      marginBottom: 5,
    },
    progressBar: {
      height: 5,
      backgroundColor: '#2D2D2D',
      borderRadius: 5,
      overflow: 'hidden',
    },
    progressFill: {
      height: '100%',
      backgroundColor: '#BB86FC',
    },
    moveButtons: {
      flexDirection: 'row',
      marginRight: 10,
    },
    moveButton: {
      backgroundColor: '#BB86FC',
      padding: 5,
      borderRadius: 4,
      marginHorizontal: 2,
    },
    moveButtonText: {
      color: '#FFFFFF',
      fontSize: 14,
    },
  
    // History
    historyList: {
      maxHeight: 300,
      marginTop: 10,
      width: '100%',
    },
    historyItem: {
      padding: 10,
      borderBottomWidth: 1,
      borderBottomColor: '#2D2D2D',
    },
    historyWord: {
      color: '#BB86FC',
      fontSize: 16,
      fontWeight: 'bold',
    },
    historyReading: {
      color: '#666666',
      fontSize: 14,
    },
    historyTimestamp: {
      color: '#666666',
      fontSize: 12,
      marginTop: 2,
    },
  
    // Buttons & Controls
    buttonContainer: {
      flexDirection: "row",
      justifyContent: "space-between",
      paddingHorizontal: 0,
      paddingBottom: 20,
      paddingTop: 10,
      position: 'absolute',
      bottom: 40,
      left: 20,
      right: 20,
      zIndex: 10, // Lower than sidebar
    },
    captureButton: {
      flex: 1,
      marginRight: 5,
    },
    galleryButton: {
      flex: 1,
      marginLeft: 5,
    },
    modeSelector: {
      flexDirection: 'row',
      justifyContent: 'center',
      position: 'absolute',
      bottom: 0,
      left: 0,
      right: 0,
      backgroundColor: '#f7f7f7',
      borderTopWidth: 1,
      borderTopColor: '#3700B3',
      zIndex: 10, // Lower than sidebar
    },
    modeButton: {
      padding: 12,
      paddingHorizontal: 30,
      borderBottomWidth: 2,
      borderBottomColor: 'transparent',
      marginHorizontal: 10,
    },
    activeMode: {
      borderBottomColor: '#BB86FC',
    },
    modeButtonText: {
      color: '#BB86FC',
      fontSize: 16,
      fontWeight: 'bold',
    },
    switchContainer: {
      flexDirection: "row",
      alignItems: "center",
      marginVertical: -10,
      justifyContent: 'space-between',
      paddingRight: 20,
    },
    switchLabel: {
      color: "#000000",
      marginRight: 10,
      fontSize: 20,
    },
    switchWrapper: {
      marginTop: 5,
    },
    primaryButton: {
      backgroundColor: '#BB86FC',
      padding: 14,
      borderRadius: 8,
      alignItems: 'center',
    },
    primaryButtonText: {
      color: '#ffffff',
      fontSize: 16,
      fontWeight: 'bold',
    },
    secondaryButton: {
      backgroundColor: '#2D2D2D',
      padding: 8,
      borderRadius: 5,
      marginTop: 2,
      marginRight: 0,
    },
    secondaryButtonText: {
      color: '#FFFFFF',
      fontSize: 14,
      fontWeight: 'bold',
    },
    closeButton: {
      padding: 8,
    },
    closeButtonText: {
      fontSize: 20,
      color: '#2e2e2e',
    },
  
    // Error States
    errorText: {
      color: "#FF4444",
      fontSize: 16,
      marginTop: 10,
    },
    deckItem: {
      padding: 10,
      backgroundColor: '#ededed',
      borderRadius: 5,
      marginBottom: 10,
    },
    deckName: {
      color: '#2D2D2D',
      fontSize: 16,
      fontWeight: 'bold',
    },
    deckStats: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginTop: 5,
    },
    deckCount: {
      color: '#2D2D2D',
      fontSize: 12,
    },
    dueCount: {
      color: '#BB86FC',
      fontSize: 12,
      fontWeight: 'bold',
    },
    historyItemContent: {
      flex: 1,
      flexDirection: 'column',
      overflow: 'hidden',
    },
    disabledMainContent: {
      opacity: 0.5,
    },
    modalReading: {
      fontSize: 16,
      color: '#BB86FC',
      marginTop: 5,
      textAlign: 'left',
      flexShrink: 1,
    },
    modalText: {
      fontSize: 16,
      color: '#2e2e2e',
      lineHeight: 24,
    },
    section: {
      marginBottom: 20,
      paddingBottom: 20,
      borderBottomWidth: 1,
      borderBottomColor: '#2D2D2D',
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: 'bold',
      color: '#BB86FC',
    },
    noDictionariesText: {
      color: '#AAAAAA',
      fontStyle: 'italic',
      textAlign: 'center',
      marginTop: 10,
    },
    statusContainer: {
      marginTop: 4,
    },
    dictionaryError: {
      color: '#FF4444',
      fontSize: 12,
      marginTop: 4,
    },
    disabledButton: {
      opacity: 0.5,
    },
    reviewDefinitionContainer: {
      flex: 1,
      marginBottom: 20,
    },
    reviewDefinition: {
      fontSize: 16,
      color: '#2d2d2d',
      lineHeight: 24,
    },
    wordListContainer: {
      position: 'absolute',
      top: 50,
      left: 0,
      right: 0,
      backgroundColor: '#ededed',
      borderWidth: 1,
      borderColor: '#3700B3',
      borderRadius: 5,
      maxHeight: 620,
      zIndex: 10, // Lower than sidebar's zIndex (100)
    },
    wordList: {
      flex: 1,
    },
    wordListItem: {
      padding: 10,
      borderBottomWidth: 1,
      borderBottomColor: '#2D2D2D',
    },
    wordListText: {
      color: '#BB86FC',
      fontSize: 16,
    },
    srsContainer: {
      flex: 1,
    },
    noDecksText: {
      color: '#AAAAAA',
      textAlign: 'center',
      marginTop: 20,
      fontSize: 16,
    },
    deckSRSButton: {
      backgroundColor: '#3700B3',
      padding: 10,
      borderRadius: 5,
      marginBottom: 5,
      alignItems: 'center',
    },
    deckSRSButtonText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
    },
    backButton: {
      padding: 10,
      marginBottom: 10,
    },
    backButtonText: {
      color: '#BB86FC',
      fontSize: 16,
    },
    wordItem: {
      padding: 15,
      backgroundColor: '#ededed',
      borderRadius: 8,
      marginBottom: 10,
      borderWidth: 1,
      borderColor: '#2D2D2D',
    },
    wordItemText: {
      color: '#BB86FC',
      fontSize: 18,
      fontWeight: 'bold',
    },
    wordItemReading: {
      color: '#2e2e2e',
      fontSize: 14,
      marginTop: 5,
    },
    wordItemHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 5,
    },
    wordItemDeckName: {
      fontSize: 12,
      color: '#ffffff',
      backgroundColor: '#3700B3',
      paddingHorizontal: 8,
      paddingVertical: 2,
      borderRadius: 10,
    },
    deckActions: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: 10,
    },
    currentDeckItem: {
      borderColor: '#BB86FC',
      borderWidth: 1,
    },
    currentDeckIndicator: {
      color: '#BB86FC',
      fontSize: 12,
      marginTop: 5,
      textAlign: 'center',
    },
    // Input
    modalInput: {
      backgroundColor: '#ededed',
      color: '#2D2D2D',
      padding: 14,
      borderRadius: 8,
      marginBottom: 20,
      fontSize: 16,
      borderWidth: 1,
      borderColor: '#444',
    },
    // Card Items
    cardItemContainer: {
      backgroundColor: '#ededed',
      borderRadius: 8,
      marginBottom: 12,
      overflow: 'hidden',
    },
    cardContent: {
      flexDirection: 'row',
      padding: 16,
      alignItems: 'center',
    },
    cardTextContainer: {
      flex: 1,
    },
    cardWord: {
      color: '#BB86FC',
      fontSize: 18,
      fontWeight: 'bold',
      marginBottom: 4,
    },
    cardReading: {
      color: '#2D2D2D',
      fontSize: 14,
      marginBottom: 4,
    },
    cardDueDate: {
      color: '#4CAF50',
      fontSize: 12,
    },
    // Empty State
    emptyState: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 40,
    },
    emptyStateText: {
      color: '#AAAAAA',
      fontSize: 16,
      textAlign: 'center',
    },
    answerHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      width: '100%',
      marginBottom: 10,
    },
    playButton: {
      backgroundColor: '#4a86e8',
      padding: 8,
      borderRadius: 5,
      marginLeft: 10,
      marginTop: 2,
    },
    playButtonText: {
      color: 'white',
      fontSize: 14,
      textAlign: 'center',
      fontWeight: 'bold',
    },
    cardSourceText: {
    color: '#888888',
    fontSize: 12,
    marginTop: 4,
    fontStyle: 'italic',
  },
  componentsContainer: {
    marginTop: 20,
    marginBottom: 20,
  },
  componentsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  componentsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  kanjiButton: {
    backgroundColor: '#f0f0f0',
    padding: 8,
    borderRadius: 5,
    alignItems: 'center',
    minWidth: 40,
  },
  kanjiText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  readingText: {
    fontSize: 12,
    color: '#666',
  },
  });

export default styles;
