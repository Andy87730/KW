# -*- coding: utf-8 -*-

#Import modules for UI
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout, QApplication,
    QDesktopWidget, QListWidget, QLineEdit, QPushButton, QFileDialog)
#Import modules for parsing pdf
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
#Import modules for parsing doc
import docx2txt

class Parser:
    def __init__(self, fileName):
        #Grab from string type of file
        typeFile = fileName.split('.')[-1]
        #For search method
        self.fileNameWithoutPath = str(fileName).split('/')[-1]
        #Choosing method
        if typeFile == 'pdf' or typeFile == 'PDF':
            self.allText = self.pdfParse(fileName)
        if typeFile == 'docx' or typeFile == 'DOCX':
            self.allText = self.docxParse(fileName)
        if typeFile == 'txt' or typeFile == 'TXT':
            self.allText = self.txtParse(fileName)

    '''
    Function for parsing txt file, returns matrixDoc[lines, [words, ]]
    '''
    def txtParse(self, txtName):
        #Open file
        fileTxt = open(txtName)
        matrixDoc = []
        try:
            for line in fileTxt:
                #Deleting trash tabs and empty strings (\n)
                if line == '\n':
                    continue
                line = line.strip('\t')
                line = line.strip('\n')
                matrixDoc.append(line)
        finally:
            #Close file
            fileTxt.close()
        #Cleaning from empty strings
        matrixDoc = list(filter(bool, matrixDoc))
        for i in range(len(matrixDoc)):
            matrixDoc[i] = matrixDoc[i].split(' ')
        #Mark out of file
        matrixDoc.insert(0, "$$OutOfFile")
        matrixDoc.append("$$OutOfFile")
        return matrixDoc

    '''
    Function for parsing docx file, returns matrixDoc[lines, [words, ]]
    '''
    def docxParse(self, docName):
        #Grab text from docx
        matrixDoc= docx2txt.process(docName)
        #Split to lines, then to words
        matrixDoc = matrixDoc.split('\n')
        #Cleaning from empty strings
        matrixDoc = list(filter(bool, matrixDoc))
        #Spliting on words
        for i in range(len(matrixDoc)):
            matrixDoc[i] = matrixDoc[i].split(' ')
        #Mark out of file
        matrixDoc.insert(0, "$$OutOfFile")
        matrixDoc.append("$$OutOfFile")
        return matrixDoc

    '''
    Function for parsing pdf file, returns matrixDoc[lines, [words, ]]
    '''
    def pdfParse(self, pdfName):
        #Open file in binary format
        fileInBinary = open(pdfName, 'rb')
        #Create a PDF parser object associated with the file
        parser = PDFParser(fileInBinary)
        # Create a PDF document object that stores the document structure.
        document = PDFDocument()
        # Connect the parser and document objects.
        parser.set_document(document)
        document.set_parser(parser)
        #Password for pdf
        document.initialize('')
        #Try parse document, is it allows text extraction
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        # Create a PDF resource manager object that stores shared resources.
        resourceManager = PDFResourceManager()
        #Parameters for spacing
        laparams = LAParams()
        # Create a PDF device object.
        device = PDFPageAggregator(resourceManager, laparams=laparams)
        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(resourceManager, device)
        # Process each page contained in the document.
        matrixDoc = ''
        for page in document.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                #LTTextBox it is box with text, LTTextLine ->line of text
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    matrixDoc += lt_obj.get_text()
        #Create matrix from one peace of text
        matrixDoc = matrixDoc.split('\n')
        #Cleaning from empty strings
        matrixDoc = list(filter(bool, matrixDoc))
        for i in range(len(matrixDoc)):
            matrixDoc[i] = matrixDoc[i].split(' ')
        #Close file
        fileInBinary.close()
        #Mark out of file
        matrixDoc.insert(0, "$$OutOfFile")
        matrixDoc.append("$$OutOfFile")
        return matrixDoc

    '''
    Function for searching in file word, returns name & 5 lines with word
    '''

    def search(self, keyWord):
        linesWithKeyWords = []
        #Put keyWord symbols in lowercase
        keyWord = keyWord.lower()
        #List of badSymbols , delete from words
        badSymbols = "!@.,/#$%:;'?()-"
        #Get lines from allText
        for i in range(len(self.allText)):
            #print(self.allText[i])
            #Cleaning words from badSymbols, and put in lowercase
            for word in self.allText[i]:
                for char in badSymbols:
                    word = word.replace(char , '')
                    word = word.lower()
                #Append 5 lines in result list
                if keyWord == word:
                    linesWithKeyWords.append(self.fileNameWithoutPath)
                    for j in [-2,-1,0,1,2]:
                        #Checking of ending file
                        if self.allText[i+j] == "$$OutOfFile":
                            continue
                        linesWithKeyWords.append(self.allText[i+j])
                    #TODO Delete this
                    linesWithKeyWords.append('\n')
        return linesWithKeyWords

class AppUI(QWidget):

    def __init__(self):
        #Start father (QWidget) constructor (__init__)
        super().__init__()

        self.initUI()

    '''
    Function initialize user interface
    '''
    def initUI(self):
        #Set window title, size and put in center
        self.setWindowTitle('KewWords')
        self.resize(400, 300)
        self.moveToCenter()

        #Create labels
        filesLabel = QLabel('Files')
        wordsLabel = QLabel('Words')
        #Create lists
        self.filesList = QListWidget()
        self.wordsList = QListWidget()
        #Create LineEdit (line for input information)
        self.addWordLine = QLineEdit()
        #Create buttoms
        addFileButton = QPushButton('Add file')
        addWordButton = QPushButton('+')
        searchWordsButton = QPushButton('Search words')
        #Create lists with files pathes and words
        self.listOfWords = []
        self.listOfFiles = []

        #Bind buttons
        addFileButton.clicked.connect(self.addFile)
        addWordButton.clicked.connect(self.addWord)
        searchWordsButton.clicked.connect(self.searchWords)

        #Center labels in squar in grid
        filesLabel.setAlignment(Qt.AlignCenter)
        wordsLabel.setAlignment(Qt.AlignCenter)

        #Create grid and set spacing for squars
        grid = QGridLayout()
        grid.setSpacing(10)

        #Add widget to grid
        grid.addWidget(filesLabel, 0, 0, 1, 2)
        grid.addWidget(wordsLabel, 0, 2, 1, 2)
        grid.addWidget(self.filesList, 1, 0, 1, 2)
        grid.addWidget(self.wordsList, 1, 2, 1, 2)
        grid.addWidget(addFileButton, 2, 0, 1, 2)
        grid.addWidget(self.addWordLine, 2, 2, 1, 1)
        grid.addWidget(addWordButton, 2, 3, 1, 1)
        grid.addWidget(searchWordsButton, 3, 0, 1, 4)

        #Set layout of window
        self.setLayout(grid)
        #Show window
        self.show()

    '''
    Function put window (self) in center of screen
    '''
    def moveToCenter(self):
        #Get rectangle, geometry of window
        qr = self.frameGeometry()
        #Get resolution monitor, get center dot
        cp = QDesktopWidget().availableGeometry().center()
        #Center rectangle in center window
        qr.moveCenter(cp)
        #Move topLeft dot of window in topLeft of rectangle
        self.move(qr.topLeft())

    '''
    Function open file dialog window. For choosing file and put file name in
    filesList list.
    '''
    def addFile(self):
        #Open qt dialog for choosing files to add
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filePath = QFileDialog.getOpenFileName(self, 'Open file', options=options)[0]
        #Add words for list, for parsing
        self.listOfFiles.append(str(filePath))
        fileName = str(filePath).split('/')[-1]
        self.filesList.addItem(fileName)

    '''
    Function get word from addWordLine and put word in wordsList list.
    '''
    def addWord(self):
        #Add words for list, for UI
        self.wordsList.addItem(self.addWordLine.text())
        #Add words for list, for parsing
        self.listOfWords.append(str(self.addWordLine.text()))
        #Clear addWordLine
        self.addWordLine.clear()

    '''
    Function for searching words from self.listOfWords in self.listOfFiles.
    Also open dialog window for choosing output result file and write in this
    file.
    '''
    def searchWords(self):
        #Open qt dialog for choosing directory for saving file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        resultFilePath = str(QFileDialog.getSaveFileName(self, "Save file","",
            "Text Files (*.txt)", options=options)[0])
        #Checking is it .txt, if not add type
        if ".txt" not in resultFilePath:
            resultFilePath += '.txt'

        #Open file for appending
        resultFile = open(resultFilePath, 'a+')
        #Create list of objects (Parsers)
        listOfParsers = []
        for path in self.listOfFiles:
            tempParser = Parser(path)
            listOfParsers.append(tempParser)
        #Use [obj(Parsers)] for searching words from listOfWords and write in file
        for objParser in listOfParsers:
            for word in self.listOfWords:
                for line in objParser.search(word):
                    resultFile.write('\n')
                    for w in line:
                        resultFile.write(w+" ")
        #Close file
        resultFile.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AppUI()
    sys.exit(app.exec_())
