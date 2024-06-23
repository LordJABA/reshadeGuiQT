import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QAbstractItemView, QLineEdit

class VkBasaltConfigApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('vkBasalt Config Generator')
        
        layout = QVBoxLayout()
        
        self.label = QLabel('Select Shaders Directory:')
        layout.addWidget(self.label)
        
        self.dirButton = QPushButton('Choose Directory')
        self.dirButton.clicked.connect(self.chooseDirectory)
        layout.addWidget(self.dirButton)
        
        self.shaderList = QListWidget()
        self.shaderList.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.shaderList)
        
        self.texturePathLabel = QLabel('Reshade Texture Path:')
        layout.addWidget(self.texturePathLabel)
        self.texturePathEdit = QLineEdit()
        layout.addWidget(self.texturePathEdit)
        
        self.includePathLabel = QLabel('Reshade Include Path:')
        layout.addWidget(self.includePathLabel)
        self.includePathEdit = QLineEdit()
        layout.addWidget(self.includePathEdit)
        
        self.generateButton = QPushButton('Generate Config')
        self.generateButton.clicked.connect(self.generateConfig)
        layout.addWidget(self.generateButton)
        
        self.setLayout(layout)
    
    def chooseDirectory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        directory = QFileDialog.getExistingDirectory(self, "Select Shaders Directory", "", options=options)
        if directory:
            self.loadShaders(directory)
    
    def loadShaders(self, directory):
        self.shaderList.clear()
        shaders = [f for f in os.listdir(directory) if f.endswith('.fx')]  # Add more extensions if needed
        self.shaderList.addItems(shaders)
    
    def generateConfig(self):
        try:
            selected_shaders = [item.text() for item in self.shaderList.selectedItems()]
            if not selected_shaders:
                raise ValueError("No shaders selected")
            reshade_texture_path = self.texturePathEdit.text()
            reshade_include_path = self.includePathEdit.text()
            if not reshade_texture_path or not reshade_include_path:
                raise ValueError("Reshade paths cannot be empty")
            
            config_content = self.createConfigContent(selected_shaders, reshade_texture_path, reshade_include_path)
            config_path = os.path.expanduser("~/.config/vkBasalt/vkBasalt.conf")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as file:
                file.write(config_content)
            print(f'Config file generated at {config_path}')
        except Exception as e:
            print(f"Error: {e}")
    
    def createConfigContent(self, shaders, texture_path, include_path):
        config_content = """# vkBasalt configuration
reshadeTexturePath = "{}"
reshadeIncludePath = "{}"
effects = {}
""".format(texture_path, include_path, ":".join([os.path.splitext(shader)[0] for shader in shaders]))
        for shader in shaders:
            effect_name = os.path.splitext(shader)[0]
            shader_path = os.path.join(include_path, shader)
            config_content += "{} = {}\n".format(effect_name, shader_path)
        return config_content

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VkBasaltConfigApp()
    ex.show()
    sys.exit(app.exec_())
