
class Ui_AffordableQCM(object):
    def setupUi(self, AffordableQCM):
        AffordableQCM.setObjectName("AffordableQCM")
        AffordableQCM.resize(1024, 571)
        self.centralwidget = QtWidgets.QWidget(AffordableQCM)
        self.centralwidget.setObjectName("centralwidget")
        self.recordButton = QtWidgets.QToolButton(self.centralwidget)
        self.recordButton.setGeometry(QtCore.QRect(0, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.recordButton.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/recording.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.recordButton.setIcon(icon)
        self.recordButton.setIconSize(QtCore.QSize(70, 70))
        self.recordButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.recordButton.setObjectName("recordButton")
        self.saveButton = QtWidgets.QToolButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(93, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.saveButton.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon1)
        self.saveButton.setIconSize(QtCore.QSize(70, 70))
        self.saveButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.saveButton.setObjectName("saveButton")
        self.connectionButton = QtWidgets.QToolButton(self.centralwidget)
        self.connectionButton.setGeometry(QtCore.QRect(372, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.connectionButton.setFont(font)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/usb-connection.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.connectionButton.setIcon(icon2)
        self.connectionButton.setIconSize(QtCore.QSize(70, 70))
        self.connectionButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.connectionButton.setObjectName("connectionButton")
        self.plotsButton = QtWidgets.QToolButton(self.centralwidget)
        self.plotsButton.setGeometry(QtCore.QRect(279, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.plotsButton.setFont(font)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/plot.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.plotsButton.setIcon(icon3)
        self.plotsButton.setIconSize(QtCore.QSize(70, 70))
        self.plotsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.plotsButton.setObjectName("plotsButton")
        self.tareButton = QtWidgets.QToolButton(self.centralwidget)
        self.tareButton.setGeometry(QtCore.QRect(186, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.tareButton.setFont(font)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("images/balance.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tareButton.setIcon(icon4)
        self.tareButton.setIconSize(QtCore.QSize(70, 70))
        self.tareButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.tareButton.setObjectName("tareButton")
        self.infoButton = QtWidgets.QToolButton(self.centralwidget)
        self.infoButton.setGeometry(QtCore.QRect(744, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.infoButton.setFont(font)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("images/information.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.infoButton.setIcon(icon5)
        self.infoButton.setIconSize(QtCore.QSize(70, 70))
        self.infoButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.infoButton.setObjectName("infoButton")
        self.helpButton = QtWidgets.QToolButton(self.centralwidget)
        self.helpButton.setGeometry(QtCore.QRect(651, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.helpButton.setFont(font)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("images/help.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.helpButton.setIcon(icon6)
        self.helpButton.setIconSize(QtCore.QSize(70, 70))
        self.helpButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.helpButton.setObjectName("helpButton")
        self.confirmButton = QtWidgets.QToolButton(self.centralwidget)
        self.confirmButton.setGeometry(QtCore.QRect(837, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.confirmButton.setFont(font)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("images/manual.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.confirmButton.setIcon(icon7)
        self.confirmButton.setIconSize(QtCore.QSize(70, 70))
        self.confirmButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.confirmButton.setObjectName("confirmButton")
        self.resetButton = QtWidgets.QToolButton(self.centralwidget)
        self.resetButton.setGeometry(QtCore.QRect(930, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.resetButton.setFont(font)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("images/reset.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.resetButton.setIcon(icon8)
        self.resetButton.setIconSize(QtCore.QSize(70, 70))
        self.resetButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.resetButton.setObjectName("resetButton")
        self.materialsButton = QtWidgets.QToolButton(self.centralwidget)
        self.materialsButton.setGeometry(QtCore.QRect(465, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.materialsButton.setFont(font)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("images/database.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.materialsButton.setIcon(icon9)
        self.materialsButton.setIconSize(QtCore.QSize(70, 70))
        self.materialsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.materialsButton.setObjectName("materialsButton")
        self.settingsButton = QtWidgets.QToolButton(self.centralwidget)
        self.settingsButton.setGeometry(QtCore.QRect(558, 442, 93, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.settingsButton.setFont(font)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("images/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settingsButton.setIcon(icon10)
        self.settingsButton.setIconSize(QtCore.QSize(70, 70))
        self.settingsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.settingsButton.setObjectName("settingsButton")
        self.materialComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.materialComboBox.setGeometry(QtCore.QRect(360, 30, 221, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.materialComboBox.setFont(font)
        self.materialComboBox.setObjectName("materialComboBox")
        self.materialLabel = QtWidgets.QLabel(self.centralwidget)
        self.materialLabel.setGeometry(QtCore.QRect(440, 5, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.materialLabel.setFont(font)
        self.materialLabel.setObjectName("materialLabel")
        self.frequencyLabel = QtWidgets.QLabel(self.centralwidget)
        self.frequencyLabel.setGeometry(QtCore.QRect(110, 5, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.frequencyLabel.setFont(font)
        self.frequencyLabel.setObjectName("frequencyLabel")
        self.massLabel = QtWidgets.QLabel(self.centralwidget)
        self.massLabel.setGeometry(QtCore.QRect(900, 5, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.massLabel.setFont(font)
        self.massLabel.setObjectName("massLabel")
        self.densityLabel = QtWidgets.QLabel(self.centralwidget)
        self.densityLabel.setGeometry(QtCore.QRect(700, 0, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.densityLabel.setFont(font)
        self.densityLabel.setObjectName("densityLabel")
        self.frequencyLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.frequencyLineEdit.setGeometry(QtCore.QRect(90, 30, 151, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.frequencyLineEdit.setFont(font)
        self.frequencyLineEdit.setObjectName("frequencyLineEdit")
        self.densityLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.densityLineEdit.setGeometry(QtCore.QRect(670, 30, 120, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.densityLineEdit.setFont(font)
        self.densityLineEdit.setObjectName("densityLineEdit")
        self.massLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.massLineEdit.setGeometry(QtCore.QRect(860, 30, 121, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.massLineEdit.setFont(font)
        self.massLineEdit.setObjectName("massLineEdit")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(20, 65, 1011, 361))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.stackedWidget.setFont(font)
        self.stackedWidget.setObjectName("stackedWidget")
        self.mainPage = QtWidgets.QWidget()
        self.mainPage.setObjectName("mainPage")
        self.thicknessLabel = QtWidgets.QLabel(self.mainPage)
        self.thicknessLabel.setGeometry(QtCore.QRect(10, 124, 431, 51))
        font = QtGui.QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.thicknessLabel.setFont(font)
        self.thicknessLabel.setObjectName("thicknessLabel")
        self.frequencyBigLabel = QtWidgets.QLabel(self.mainPage)
        self.frequencyBigLabel.setGeometry(QtCore.QRect(10, 246, 431, 81))
        font = QtGui.QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.frequencyBigLabel.setFont(font)
        self.frequencyBigLabel.setObjectName("frequencyBigLabel")
        self.lcdNumber = QtWidgets.QLCDNumber(self.mainPage)
        self.lcdNumber.setGeometry(QtCore.QRect(410, 110, 541, 91))
        self.lcdNumber.setDigitCount(7)
        self.lcdNumber.setObjectName("lcdNumber")
        self.lcdNumber_2 = QtWidgets.QLCDNumber(self.mainPage)
        self.lcdNumber_2.setGeometry(QtCore.QRect(410, 230, 541, 91))
        self.lcdNumber_2.setDigitCount(7)
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.stackedWidget.addWidget(self.mainPage)
        self.savePage = QtWidgets.QWidget()
        self.savePage.setObjectName("savePage")
        self.pathLineEdit = QtWidgets.QLineEdit(self.savePage)
        self.pathLineEdit.setGeometry(QtCore.QRect(430, 120, 391, 101))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pathLineEdit.setFont(font)
        self.pathLineEdit.setObjectName("pathLineEdit")
        self.appendRadioButton = QtWidgets.QRadioButton(self.savePage)
        self.appendRadioButton.setGeometry(QtCore.QRect(440, 240, 191, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.appendRadioButton.setFont(font)
        self.appendRadioButton.setObjectName("appendRadioButton")
        self.overwriteRadioButton = QtWidgets.QRadioButton(self.savePage)
        self.overwriteRadioButton.setGeometry(QtCore.QRect(680, 240, 171, 81))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.overwriteRadioButton.setFont(font)
        self.overwriteRadioButton.setObjectName("overwriteRadioButton")
        self.frequencyCheckbox = QtWidgets.QCheckBox(self.savePage)
        self.frequencyCheckbox.setGeometry(QtCore.QRect(41, 92, 261, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.frequencyCheckbox.setFont(font)
        self.frequencyCheckbox.setObjectName("frequencyCheckbox")
        self.frequencyChangeCheckbox = QtWidgets.QCheckBox(self.savePage)
        self.frequencyChangeCheckbox.setGeometry(QtCore.QRect(41, 132, 271, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.frequencyChangeCheckbox.setFont(font)
        self.frequencyChangeCheckbox.setObjectName("frequencyChangeCheckbox")
        self.frequencyROCCheckbox = QtWidgets.QCheckBox(self.savePage)
        self.frequencyROCCheckbox.setGeometry(QtCore.QRect(41, 169, 291, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.frequencyROCCheckbox.setFont(font)
        self.frequencyROCCheckbox.setObjectName("frequencyROCCheckbox")
        self.thicknessCheckbox = QtWidgets.QCheckBox(self.savePage)
        self.thicknessCheckbox.setGeometry(QtCore.QRect(41, 219, 231, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.thicknessCheckbox.setFont(font)
        self.thicknessCheckbox.setObjectName("thicknessCheckbox")
        self.rateOfDepositionCheckbox = QtWidgets.QCheckBox(self.savePage)
        self.rateOfDepositionCheckbox.setGeometry(QtCore.QRect(41, 259, 195, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.rateOfDepositionCheckbox.setFont(font)
        self.rateOfDepositionCheckbox.setObjectName("rateOfDepositionCheckbox")
        self.saveQuestionLabel = QtWidgets.QLabel(self.savePage)
        self.saveQuestionLabel.setGeometry(QtCore.QRect(41, 50, 307, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.saveQuestionLabel.setFont(font)
        self.saveQuestionLabel.setObjectName("saveQuestionLabel")
        self.saveQuestionLabel_2 = QtWidgets.QLabel(self.savePage)
        self.saveQuestionLabel_2.setGeometry(QtCore.QRect(410, 40, 421, 49))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.saveQuestionLabel_2.setFont(font)
        self.saveQuestionLabel_2.setObjectName("saveQuestionLabel_2")
        self.stackedWidget.addWidget(self.savePage)
        self.materialsPage = QtWidgets.QWidget()
        self.materialsPage.setObjectName("materialsPage")
        self.materialsListWidget = QtWidgets.QListWidget(self.materialsPage)
        self.materialsListWidget.setGeometry(QtCore.QRect(60, 20, 256, 311))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.materialsListWidget.setFont(font)
        self.materialsListWidget.setObjectName("materialsListWidget")
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.materialsListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.materialsListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.materialsListWidget.addItem(item)
        self.addButton = QtWidgets.QPushButton(self.materialsPage)
        self.addButton.setGeometry(QtCore.QRect(410, 20, 151, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.addButton.setFont(font)
        self.addButton.setObjectName("addButton")
        self.editButton = QtWidgets.QPushButton(self.materialsPage)
        self.editButton.setGeometry(QtCore.QRect(410, 130, 151, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.editButton.setFont(font)
        self.editButton.setObjectName("editButton")
        self.deleteButton = QtWidgets.QPushButton(self.materialsPage)
        self.deleteButton.setGeometry(QtCore.QRect(410, 250, 151, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.deleteButton.setFont(font)
        self.deleteButton.setObjectName("deleteButton")
        self.materialEditLineEdit = QtWidgets.QLineEdit(self.materialsPage)
        self.materialEditLineEdit.setGeometry(QtCore.QRect(690, 60, 281, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.materialEditLineEdit.setFont(font)
        self.materialEditLineEdit.setObjectName("materialEditLineEdit")
        self.densityEditLineEdit = QtWidgets.QLineEdit(self.materialsPage)
        self.densityEditLineEdit.setGeometry(QtCore.QRect(690, 260, 291, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.densityEditLineEdit.setFont(font)
        self.densityEditLineEdit.setObjectName("densityEditLineEdit")
        self.materialEditLabel = QtWidgets.QLabel(self.materialsPage)
        self.materialEditLabel.setGeometry(QtCore.QRect(690, 20, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.materialEditLabel.setFont(font)
        self.materialEditLabel.setObjectName("materialEditLabel")
        self.densityEditLabel = QtWidgets.QLabel(self.materialsPage)
        self.densityEditLabel.setGeometry(QtCore.QRect(690, 220, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.densityEditLabel.setFont(font)
        self.densityEditLabel.setObjectName("densityEditLabel")
        self.stackedWidget.addWidget(self.materialsPage)
        self.plotPage = QtWidgets.QWidget()
        self.plotPage.setObjectName("plotPage")
        self.tabWidget = QtWidgets.QTabWidget(self.plotPage)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1001, 361))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.thicknessTab = QtWidgets.QWidget()
        self.thicknessTab.setObjectName("thicknessTab")
        self.plt_4_thickness = GraphicsLayoutWidget(self.thicknessTab)
        self.plt_4_thickness.setGeometry(QtCore.QRect(0, 0, 1000, 321))
        self.plt_4_thickness.setAutoFillBackground(False)
        self.plt_4_thickness.setStyleSheet("border: 0px;")
        self.plt_4_thickness.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plt_4_thickness.setFrameShadow(QtWidgets.QFrame.Plain)
        self.plt_4_thickness.setLineWidth(0)
        self.plt_4_thickness.setObjectName("plt_4_thickness")
        self.tabWidget.addTab(self.thicknessTab, "")
        self.freqTab = QtWidgets.QWidget()
        self.freqTab.setObjectName("freqTab")
        self.plt6_Freq = GraphicsLayoutWidget(self.freqTab)
        self.plt6_Freq.setGeometry(QtCore.QRect(0, 0, 1000, 321))
        self.plt6_Freq.setAutoFillBackground(False)
        self.plt6_Freq.setStyleSheet("border: 0px;")
        self.plt6_Freq.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plt6_Freq.setFrameShadow(QtWidgets.QFrame.Plain)
        self.plt6_Freq.setLineWidth(0)
        self.plt6_Freq.setObjectName("plt6_Freq")
        self.tabWidget.addTab(self.freqTab, "")
        self.freqChangeTab = QtWidgets.QWidget()
        self.freqChangeTab.setObjectName("freqChangeTab")
        self.plt_2_changeFreq = GraphicsLayoutWidget(self.freqChangeTab)
        self.plt_2_changeFreq.setGeometry(QtCore.QRect(0, 0, 1000, 321))
        self.plt_2_changeFreq.setAutoFillBackground(False)
        self.plt_2_changeFreq.setStyleSheet("border: 0px;")
        self.plt_2_changeFreq.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plt_2_changeFreq.setFrameShadow(QtWidgets.QFrame.Plain)
        self.plt_2_changeFreq.setLineWidth(0)
        self.plt_2_changeFreq.setObjectName("plt_2_changeFreq")
        self.tabWidget.addTab(self.freqChangeTab, "")
        self.stackedWidget.addWidget(self.plotPage)
        self.connectPage = QtWidgets.QWidget()
        self.connectPage.setObjectName("connectPage")
        self.RTGraphWidget = QtWidgets.QWidget(self.connectPage)
        self.RTGraphWidget.setGeometry(QtCore.QRect(0, 170, 781, 191))
        self.RTGraphWidget.setObjectName("RTGraphWidget")
        self.Layout_controls = QtWidgets.QGridLayout(self.RTGraphWidget)
        self.Layout_controls.setContentsMargins(0, 0, 0, 0)
        self.Layout_controls.setObjectName("Layout_controls")
        self.pButton_Stop = QtWidgets.QPushButton(self.RTGraphWidget)
        self.pButton_Stop.setObjectName("pButton_Stop")
        self.Layout_controls.addWidget(self.pButton_Stop, 1, 3, 1, 1)
        self.cBox_Port = QtWidgets.QComboBox(self.RTGraphWidget)
        self.cBox_Port.setEditable(True)
        self.cBox_Port.setObjectName("cBox_Port")
        self.Layout_controls.addWidget(self.cBox_Port, 0, 1, 1, 1)
        self.cBox_Source = QtWidgets.QComboBox(self.RTGraphWidget)
        self.cBox_Source.setObjectName("cBox_Source")
        self.Layout_controls.addWidget(self.cBox_Source, 0, 0, 1, 1)
        self.pButton_Start = QtWidgets.QPushButton(self.RTGraphWidget)
        self.pButton_Start.setMinimumSize(QtCore.QSize(0, 0))
        self.pButton_Start.setObjectName("pButton_Start")
        self.Layout_controls.addWidget(self.pButton_Start, 0, 3, 1, 1)
        self.cBox_Speed = QtWidgets.QComboBox(self.RTGraphWidget)
        self.cBox_Speed.setEditable(True)
        self.cBox_Speed.setObjectName("cBox_Speed")
        self.Layout_controls.addWidget(self.cBox_Speed, 1, 1, 1, 1)
        self.sBox_Samples = QtWidgets.QSpinBox(self.RTGraphWidget)
        self.sBox_Samples.setMinimum(1)
        self.sBox_Samples.setMaximum(100000)
        self.sBox_Samples.setProperty("value", 500)
        self.sBox_Samples.setObjectName("sBox_Samples")
        self.Layout_controls.addWidget(self.sBox_Samples, 0, 2, 1, 1)
        self.plt = GraphicsLayoutWidget(self.connectPage)
        self.plt.setGeometry(QtCore.QRect(0, 10, 1000, 200))
        self.plt.setAutoFillBackground(False)
        self.plt.setStyleSheet("border: 0px;")
        self.plt.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plt.setFrameShadow(QtWidgets.QFrame.Plain)
        self.plt.setLineWidth(0)
        self.plt.setObjectName("plt")
        self.chBox_export = QtWidgets.QCheckBox(self.connectPage)
        self.chBox_export.setEnabled(True)
        self.chBox_export.setGeometry(QtCore.QRect(430, 110, 186, 28))
        self.chBox_export.setObjectName("chBox_export")
        self.chBox_export.raise_()
        self.RTGraphWidget.raise_()
        self.plt.raise_()
        self.stackedWidget.addWidget(self.connectPage)
        self.settingsPage = QtWidgets.QWidget()
        self.settingsPage.setObjectName("settingsPage")
        self.densityUnitLabel = QtWidgets.QLabel(self.settingsPage)
        self.densityUnitLabel.setGeometry(QtCore.QRect(42, 160, 241, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.densityUnitLabel.setFont(font)
        self.densityUnitLabel.setObjectName("densityUnitLabel")
        self.densityUnitComboBox = QtWidgets.QComboBox(self.settingsPage)
        self.densityUnitComboBox.setGeometry(QtCore.QRect(336, 100, 191, 36))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.densityUnitComboBox.setFont(font)
        self.densityUnitComboBox.setObjectName("densityUnitComboBox")
        self.massUnitLabel = QtWidgets.QLabel(self.settingsPage)
        self.massUnitLabel.setGeometry(QtCore.QRect(42, 110, 251, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.massUnitLabel.setFont(font)
        self.massUnitLabel.setObjectName("massUnitLabel")
        self.massUnitComboBox = QtWidgets.QComboBox(self.settingsPage)
        self.massUnitComboBox.setGeometry(QtCore.QRect(336, 160, 191, 36))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.massUnitComboBox.setFont(font)
        self.massUnitComboBox.setObjectName("massUnitComboBox")
        self.thicknessUnitComboBox = QtWidgets.QComboBox(self.settingsPage)
        self.thicknessUnitComboBox.setGeometry(QtCore.QRect(336, 220, 191, 36))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.thicknessUnitComboBox.setFont(font)
        self.thicknessUnitComboBox.setObjectName("thicknessUnitComboBox")
        self.thicknessUnitLabel = QtWidgets.QLabel(self.settingsPage)
        self.thicknessUnitLabel.setGeometry(QtCore.QRect(42, 220, 251, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.thicknessUnitLabel.setFont(font)
        self.thicknessUnitLabel.setObjectName("thicknessUnitLabel")
        self.rateOfDepositionUnitLabel = QtWidgets.QLabel(self.settingsPage)
        self.rateOfDepositionUnitLabel.setGeometry(QtCore.QRect(42, 280, 261, 28))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.rateOfDepositionUnitLabel.setFont(font)
        self.rateOfDepositionUnitLabel.setObjectName("rateOfDepositionUnitLabel")
        self.rateOfDepositionComboBox = QtWidgets.QComboBox(self.settingsPage)
        self.rateOfDepositionComboBox.setGeometry(QtCore.QRect(336, 280, 191, 36))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.rateOfDepositionComboBox.setFont(font)
        self.rateOfDepositionComboBox.setObjectName("rateOfDepositionComboBox")
        self.toolingFactorSpinBox = QtWidgets.QDoubleSpinBox(self.settingsPage)
        self.toolingFactorSpinBox.setGeometry(QtCore.QRect(830, 160, 121, 91))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.toolingFactorSpinBox.setFont(font)
        self.toolingFactorSpinBox.setMaximum(100.0)
        self.toolingFactorSpinBox.setSingleStep(0.1)
        self.toolingFactorSpinBox.setProperty("value", 100.0)
        self.toolingFactorSpinBox.setObjectName("toolingFactorSpinBox")
        self.toolingFactorLabel = QtWidgets.QLabel(self.settingsPage)
        self.toolingFactorLabel.setGeometry(QtCore.QRect(630, 160, 121, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.toolingFactorLabel.setFont(font)
        self.toolingFactorLabel.setObjectName("toolingFactorLabel")
        self.aliasingLabel = QtWidgets.QLabel(self.settingsPage)
        self.aliasingLabel.setGeometry(QtCore.QRect(630, 250, 251, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.aliasingLabel.setFont(font)
        self.aliasingLabel.setObjectName("aliasingLabel")
        self.aliasingNOButton = QtWidgets.QRadioButton(self.settingsPage)
        self.aliasingNOButton.setGeometry(QtCore.QRect(900, 251, 91, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.aliasingNOButton.setFont(font)
        self.aliasingNOButton.setObjectName("aliasingNOButton")
        self.aliasingYESButton = QtWidgets.QRadioButton(self.settingsPage)
        self.aliasingYESButton.setGeometry(QtCore.QRect(900, 300, 91, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.aliasingYESButton.setFont(font)
        self.aliasingYESButton.setObjectName("aliasingYESButton")
        self.stackedWidget.addWidget(self.settingsPage)
        self.helpPage = QtWidgets.QWidget()
        self.helpPage.setObjectName("helpPage")
        self.stackedWidget.addWidget(self.helpPage)
        self.infoPage = QtWidgets.QWidget()
        self.infoPage.setObjectName("infoPage")
        self.authorsLabel = QtWidgets.QLabel(self.infoPage)
        self.authorsLabel.setGeometry(QtCore.QRect(0, 0, 1031, 361))
        self.authorsLabel.setObjectName("authorsLabel")
        self.stackedWidget.addWidget(self.infoPage)
        AffordableQCM.setCentralWidget(self.centralwidget)

        self.retranslateUi(AffordableQCM)
        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(AffordableQCM)

    def retranslateUi(self, AffordableQCM):
        _translate = QtCore.QCoreApplication.translate
        AffordableQCM.setWindowTitle(_translate("AffordableQCM", "MainWindow"))
        self.recordButton.setText(_translate("AffordableQCM", "RECORD"))
        self.saveButton.setText(_translate("AffordableQCM", "SAVE"))
        self.connectionButton.setText(_translate("AffordableQCM", "CONNECT"))
        self.plotsButton.setText(_translate("AffordableQCM", "PLOTS"))
        self.tareButton.setText(_translate("AffordableQCM", "TARE"))
        self.infoButton.setText(_translate("AffordableQCM", "INFO"))
        self.helpButton.setText(_translate("AffordableQCM", "HELP"))
        self.confirmButton.setText(_translate("AffordableQCM", "CONFIRM"))
        self.resetButton.setText(_translate("AffordableQCM", "RESET"))
        self.materialsButton.setText(_translate("AffordableQCM", "MATERIALS"))
        self.settingsButton.setText(_translate("AffordableQCM", "SETTINGS"))
        self.materialLabel.setText(_translate("AffordableQCM", "Material"))
        self.frequencyLabel.setText(_translate("AffordableQCM", "Frequency"))
        self.massLabel.setText(_translate("AffordableQCM", "Mass"))
        self.densityLabel.setText(_translate("AffordableQCM", "Density"))
        self.thicknessLabel.setText(_translate("AffordableQCM", "Thickness [nm]"))
        self.frequencyBigLabel.setText(_translate("AffordableQCM", "FREQUENCY"))
        self.appendRadioButton.setText(_translate("AffordableQCM", "Append?"))
        self.overwriteRadioButton.setText(_translate("AffordableQCM", "Overwrite?"))
        self.frequencyCheckbox.setText(_translate("AffordableQCM", "Frequency"))
        self.frequencyChangeCheckbox.setText(_translate("AffordableQCM", "Frequency Change"))
        self.frequencyROCCheckbox.setText(_translate("AffordableQCM", "Frequency Rate of Change"))
        self.thicknessCheckbox.setText(_translate("AffordableQCM", "Thickness"))
        self.rateOfDepositionCheckbox.setText(_translate("AffordableQCM", "Rate of deposition"))
        self.saveQuestionLabel.setText(_translate("AffordableQCM", "Which data do you want to save?"))
        self.saveQuestionLabel_2.setText(_translate("AffordableQCM", "Path to file (e.g.) /data/20221001_gold01.csv"))
        __sortingEnabled = self.materialsListWidget.isSortingEnabled()
        self.materialsListWidget.setSortingEnabled(False)
        item = self.materialsListWidget.item(0)
        item.setText(_translate("AffordableQCM", "Gold"))
        item = self.materialsListWidget.item(1)
        item.setText(_translate("AffordableQCM", "Platinum"))
        item = self.materialsListWidget.item(2)
        item.setText(_translate("AffordableQCM", "Carbon"))
        self.materialsListWidget.setSortingEnabled(__sortingEnabled)
        self.addButton.setText(_translate("AffordableQCM", "Add"))
        self.editButton.setText(_translate("AffordableQCM", "Edit"))
        self.deleteButton.setText(_translate("AffordableQCM", "Delete"))
        self.materialEditLabel.setText(_translate("AffordableQCM", "Material name"))
        self.densityEditLabel.setText(_translate("AffordableQCM", "Density"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.thicknessTab), _translate("AffordableQCM", "Thickness"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.freqTab), _translate("AffordableQCM", "Absolute frequency"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.freqChangeTab), _translate("AffordableQCM", "Frequency change"))
        self.pButton_Stop.setText(_translate("AffordableQCM", "Stop"))
        self.pButton_Start.setText(_translate("AffordableQCM", "Start"))
        self.sBox_Samples.setSuffix(_translate("AffordableQCM", " samples"))
        self.sBox_Samples.setPrefix(_translate("AffordableQCM", "Show "))
        self.chBox_export.setText(_translate("AffordableQCM", "Export to CSV"))
        self.densityUnitLabel.setText(_translate("AffordableQCM", "Density unit"))
        self.massUnitLabel.setText(_translate("AffordableQCM", "Mass unit"))
        self.thicknessUnitLabel.setText(_translate("AffordableQCM", "Thickness unit"))
        self.rateOfDepositionUnitLabel.setText(_translate("AffordableQCM", "Rate of deposition unit"))
        self.toolingFactorLabel.setText(_translate("AffordableQCM", "<html><head/><body><p>Tooling<br/>Factor</p></body></html>"))
        self.aliasingLabel.setText(_translate("AffordableQCM", "<html><head/><body><p>Quartz frequency &gt; 8MHz?</p></body></html>"))
        self.aliasingNOButton.setText(_translate("AffordableQCM", "NO"))
        self.aliasingYESButton.setText(_translate("AffordableQCM", "YES"))
        self.authorsLabel.setText(_translate("AffordableQCM", "<html><head/><body><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">You should have received a copy of the GNU General Public License along with this program.</span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">If not, see https://www.gnu.org/licenses/ </span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License</span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.</span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">The app was created as a part of an engineering thesis: Design of the gauge for the sputtered coating thickness measurement.&quot;</span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">Copyright (C) 2022 Adrian Matusiak</span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;</span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. </span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">See the GNU General Public License for more details.</span></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">The software contains code written by Marco Mauro (same license) and code by Sebastián Sepúlveda (MIT License).</span></pre><pre style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier New\'; background-color:#1e1e1e;\"><br/></pre><pre style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#1e1e1e;\"><span style=\" font-family:\'Consolas\',\'Courier New\',\'monospace\'; font-size:14px; color:#ce9178;\">Icons made by https://www.freepik.com Freepik from https://www.flaticon.com/</span></pre><pre style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier New\'; background-color:#1e1e1e;\"><br/></pre><p><br/></p></body></html>"))
