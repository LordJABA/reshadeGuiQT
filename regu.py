import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QAbstractItemView, QSlider, QCheckBox, QLineEdit
)
from PyQt5.QtCore import Qt

class VkBasaltConfigApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('vkBasalt Config Generator')
        
        layout = QVBoxLayout()
        
        self.label = QLabel('Available Shaders:')
        layout.addWidget(self.label)
        
        self.shaderList = QListWidget()
        self.shaderList.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.shaderList)
        
        home_directory = os.path.expanduser("~")
        shaders_directory = os.path.join(home_directory, "reshade-shaders/Shaders")
        self.loadShaders(shaders_directory)

        # Sliders and Toggles for options
        self.casSharpnessSlider = self.createSlider("CAS Sharpness", 0, 100, 40)
        self.dlsSharpnessSlider = self.createSlider("DLS Sharpness", 0, 100, 50)
        self.dlsDenoiseSlider = self.createSlider("DLS Denoise", 0, 100, 17)
        self.fxaaQualitySubpixSlider = self.createSlider("FXAA Quality Subpix", 0, 100, 75)
        self.fxaaQualityEdgeThresholdSlider = self.createSlider("FXAA Quality Edge Threshold", 0, 100, 12)
        self.fxaaQualityEdgeThresholdMinSlider = self.createSlider("FXAA Quality Edge Threshold Min", 0, 100, 3)
        self.smaaThresholdSlider = self.createSlider("SMAA Threshold", 0, 50, 5)
        self.smaaMaxSearchStepsSlider = self.createSlider("SMAA Max Search Steps", 0, 112, 32)
        self.smaaMaxSearchStepsDiagSlider = self.createSlider("SMAA Max Search Steps Diag", 0, 20, 16)
        self.smaaCornerRoundingSlider = self.createSlider("SMAA Corner Rounding", 0, 100, 25)
        
        self.depthCaptureToggle = self.createToggle("Depth Capture", False)
        self.enableOnLaunchToggle = self.createToggle("Enable on Launch", True)
        self.toggleKeyInput = self.createTextInput("Toggle Key", "Home")
        self.lutFileInput = self.createTextInput("LUT File", "/path/to/lut")
        
        self.generateButton = QPushButton('Generate Config')
        self.generateButton.clicked.connect(self.generateConfig)
        layout.addWidget(self.generateButton)
        
        self.setLayout(layout)
    
    def createSlider(self, label, min_val, max_val, default_val):
        layout = QVBoxLayout()
        slider_label = QLabel(f"{label}: {default_val/100.0}")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.valueChanged.connect(lambda value: slider_label.setText(f"{label}: {value/100.0}"))
        layout.addWidget(slider_label)
        layout.addWidget(slider)
        self.layout().addLayout(layout)
        return slider

    def createToggle(self, label, default_val):
        layout = QVBoxLayout()
        toggle = QCheckBox(label)
        toggle.setChecked(default_val)
        layout.addWidget(toggle)
        self.layout().addLayout(layout)
        return toggle

    def createTextInput(self, label, default_val):
        layout = QVBoxLayout()
        input_label = QLabel(label)
        input_field = QLineEdit(default_val)
        layout.addWidget(input_label)
        layout.addWidget(input_field)
        self.layout().addLayout(layout)
        return input_field

    def loadShaders(self, directory):
        self.shaderList.clear()
        shaders = [f for f in os.listdir(directory) if f.endswith('.fx')]  # Add more extensions if needed
        self.shaderList.addItems(shaders)
    
    def generateConfig(self):
        try:
            selected_shaders = [item.text() for item in self.shaderList.selectedItems()]
            if not selected_shaders:
                raise ValueError("No shaders selected")
            
            home_directory = os.path.expanduser("~")
            reshade_texture_path = os.path.join(home_directory, "reshade-shaders/Textures")
            reshade_include_path = os.path.join(home_directory, "reshade-shaders/Shaders")
            
            config_content = self.createConfigContent(
                selected_shaders, 
                reshade_texture_path, 
                reshade_include_path,
                self.casSharpnessSlider.value(),
                self.dlsSharpnessSlider.value(),
                self.dlsDenoiseSlider.value(),
                self.fxaaQualitySubpixSlider.value(),
                self.fxaaQualityEdgeThresholdSlider.value(),
                self.fxaaQualityEdgeThresholdMinSlider.value(),
                self.smaaThresholdSlider.value(),
                self.smaaMaxSearchStepsSlider.value(),
                self.smaaMaxSearchStepsDiagSlider.value(),
                self.smaaCornerRoundingSlider.value(),
                self.depthCaptureToggle.isChecked(),
                self.enableOnLaunchToggle.isChecked(),
                self.toggleKeyInput.text(),
                self.lutFileInput.text()
            )
            config_path = os.path.expanduser("~/.config/vkBasalt/vkBasalt.conf")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as file:
                file.write(config_content)
            print(f'Config file generated at {config_path}')
        except Exception as e:
            print(f"Error: {e}")
    
    def createConfigContent(
        self, shaders, texture_path, include_path, 
        cas_sharpness, dls_sharpness, dls_denoise, 
        fxaa_quality_subpix, fxaa_quality_edge_threshold, fxaa_quality_edge_threshold_min,
        smaa_threshold, smaa_max_search_steps, smaa_max_search_steps_diag, smaa_corner_rounding,
        depth_capture, enable_on_launch, toggle_key, lut_file
    ):
        config_content = f"""#effects is a colon separated list of effects to use
#e.g.: effects = fxaa:cas
#effects will be run in order from left to right
#one effect can be run multiple times e.g. smaa:smaa:cas
#cas    - Contrast Adaptive Sharpening
#dls    - Denoised Luma Sharpening
#fxaa   - Fast Approximate Anti-Aliasing
#smaa   - Enhanced Subpixel Morphological Antialiasing
#lut    - Color LookUp Table
effects = {':'.join([os.path.splitext(shader)[0] for shader in shaders])}

reshadeTexturePath = "{texture_path}"
reshadeIncludePath = "{include_path}"
depthCapture = {"on" if depth_capture else "off"}

#toggleKey toggles the effects on/off
toggleKey = {toggle_key}

#enableOnLaunch sets if the effects are enabled when started
enableOnLaunch = {"True" if enable_on_launch else "False"}

#casSharpness specifies the amount of sharpening in the CAS shader.
#0.0 less sharp, less artefacts, but not off
#1.0 maximum sharp more artefacts
#Everything in between is possible
#negative values sharpen even less, up to -1.0 make a visible difference
casSharpness = {cas_sharpness / 100.0}

#dlsSharpness specifies the amount of sharpening in the Denoised Luma Sharpening shader.
#Increase to sharpen details within the image.
#0.0 less sharp, less artefacts, but not off
#1.0 maximum sharp more artefacts
dlsSharpness = {dls_sharpness / 100.0}

#dlsDenoise specifies the amount of denoising in the Denoised Luma Sharpening shader.
#Increase to limit how intensely film grain within the image gets sharpened.
#0.0 min
#1.0 max
dlsDenoise = {dls_denoise / 100.0}

#fxaaQualitySubpix can effect sharpness.
#1.00 - upper limit (softer)
#0.75 - default amount of filtering
#0.50 - lower limit (sharper, less sub-pixel aliasing removal)
#0.25 - almost off
#0.00 - completely off
fxaaQualitySubpix = {fxaa_quality_subpix / 100.0}

#fxaaQualityEdgeThreshold is the minimum amount of local contrast required to apply algorithm.
#0.333 - too little (faster)
#0.250 - low quality
#0.166 - default
#0.125 - high quality 
#0.063 - overkill (slower)
fxaaQualityEdgeThreshold = {fxaa_quality_edge_threshold / 100.0}

#fxaaQualityEdgeThresholdMin trims the algorithm from processing darks.
#0.0833 - upper limit (default, the start of visible unfiltered edges)
#0.0625 - high quality (faster)
#0.0312 - visible limit (slower)
#Special notes: due to the current implementation you
#Likely want to set this to zero.
#As colors that are mostly not-green
#will appear very dark in the green channel!
#Tune by looking at mostly non-green content,
#then start at zero and increase until aliasing is a problem.
fxaaQualityEdgeThresholdMin = {fxaa_quality_edge_threshold_min / 100.0}

#smaaEdgeDetection changes the edge detection shader
#luma  - default
#color - might catch more edges, but is more expensive
smaaEdgeDetection = luma

#smaaThreshold specifies the threshold or sensitivity to edges
#Lowering this value you will be able to detect more edges at the expense of performance.
#Range: [0, 0.5]
#0.1 is a reasonable value, and allows to catch most visible edges.
#0.05 is a rather overkill value, that allows to catch 'em all.
smaaThreshold = {smaa_threshold / 100.0}

#smaaMaxSearchSteps specifies the maximum steps performed in the horizontal/vertical pattern searches
#Range: [0, 112]
#4  - low
#8  - medium
#16 - high
#32 - ultra
smaaMaxSearchSteps = {smaa_max_search_steps}

#smaaMaxSearchStepsDiag specifies the maximum steps performed in the diagonal pattern searches
#Range: [0, 20]
#0  - low, medium
#8  - high
#16 - ultra
smaaMaxSearchStepsDiag = {smaa_max_search_steps_diag}

#smaaCornerRounding specifies how much sharp corners will be rounded
#Range: [0, 100]
#25 is a reasonable value
smaaCornerRounding = {smaa_corner_rounding}

#lutFile is the path to the LUT file that will be used
#supported are .CUBE files and .png with width == height * height
lutFile = "{lut_file}"
"""
        
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
