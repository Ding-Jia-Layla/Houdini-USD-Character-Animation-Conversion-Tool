from PySide2 import QtWidgets, QtCore
import hou
import sys
class FileSaveUI(QtWidgets.QWidget):
    def __init__(self):
        super(FileSaveUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        # 设置窗口
        
        self.setWindowTitle('File Saver')
        self.setGeometry(300, 300, 500, 100)
        self.show()
        
        # 文件路径文本框
        self.file_path_edit = QtWidgets.QLineEdit(self)
        self.file_path_edit.setPlaceholderText("No file selected")
        self.layout.addWidget(self.file_path_edit)

        # 浏览按钮
        self.browse_button = QtWidgets.QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_file)
        self.layout.addWidget(self.browse_button)

        # 保存按钮
        self.save_button = QtWidgets.QPushButton("Save File", self)
        self.save_button.clicked.connect(self.save_file)
        self.layout.addWidget(self.save_button)
        
        # 节点获取按钮
        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setPlaceholderText("Enter SOP node path")
        self.layout.addWidget(self.line_edit)
        self.button = QtWidgets.QPushButton('Get Node', self)
        self.button.clicked.connect(self.get_node)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        
    def browse_file(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Select File", "", "USD Files (*.usda);;All Files (*)")
        if file_path:
            self.file_path_edit.setText(file_path)  # 显示文件路径

    def save_file(self):
        file_path = self.file_path_edit.text()
        if file_path:
            content = self.content_edit.toPlainText()  # 获取文本框内容
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)  # 将内容写入文件
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a file path.")
    # 拿到节点的名字
    def get_node(self):
        node_path = self.line_edit.text()
        try:
            node = hou.node(node_path)
            if node:
                hou.ui.displayMessage(f"Found node: {node.name()}")
            else:
                hou.ui.displayMessage("Node not found")
        except hou.Error as e:
            hou.ui.displayMessage(f"Error: {str(e)}")
def start_app():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = FileSaveUI()
    sys.exit(app.exec_())

start_app()
