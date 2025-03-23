import sys
import time
import numpy as np
import tensorflow as tf
import cv2
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QProgressBar
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt

class MRIReconstructionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        print("Loading model...")
        self.model = tf.keras.models.load_model("final_model_3.keras", compile=False)
        print("Model loaded successfully!")
        self.mri_data = None
        self.reconstructed_data = None

    def initUI(self):
        self.setWindowTitle("AI-Powered MRI Reconstruction")
        self.setGeometry(100, 100, 450, 400)
        
        # Set dark theme
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))  # Dark gray
        self.setPalette(palette)

        # Create buttons with styles
        button_style = """
            QPushButton {
                background-color: #3498db; 
                color: white;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        
        self.uploadButton = QPushButton("📂 Upload MRI Scan", self)
        self.uploadButton.setStyleSheet(button_style)
        self.uploadButton.clicked.connect(self.load_mri)
        
        self.reconstructButton = QPushButton("⚡ Reconstruct MRI", self)
        self.reconstructButton.setStyleSheet(button_style)
        self.reconstructButton.clicked.connect(self.reconstruct_mri)
        self.reconstructButton.setEnabled(False)
        
        self.saveButton = QPushButton("💾 Save MRI Image", self)
        self.saveButton.setStyleSheet(button_style)
        self.saveButton.clicked.connect(self.save_mri)
        self.saveButton.setEnabled(False)
        
        self.statusLabel = QLabel("🔍 Select an MRI scan to begin", self)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setFont(QFont("Arial", 11))
        self.statusLabel.setStyleSheet("color: white;")
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setStyleSheet("background: #2c3e50; color: white;")
        
        layout = QVBoxLayout()
        layout.addWidget(self.uploadButton)
        layout.addWidget(self.reconstructButton)
        layout.addWidget(self.saveButton)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.statusLabel)
        
        self.setLayout(layout)
    
    def load_mri(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MRI Scan", "", "PNG Images (*.png);;All Files (*)")
        if file_path:
            mri_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if mri_image is None:
                self.statusLabel.setText("❌ Error loading MRI image!")
                return
            
            mri_image = cv2.resize(mri_image, (640, 320))
            self.mri_data = np.expand_dims(np.expand_dims(mri_image, axis=0), axis=-1) / 255.0
            self.statusLabel.setText("✅ MRI scan loaded successfully!")
            self.reconstructButton.setEnabled(True)
    
    def reconstruct_mri(self):
        try:
            self.statusLabel.setText("⚙️ Reconstructing MRI...")
            start_time = time.time()
            reconstructed_scan = self.model.predict(self.mri_data)
            end_time = time.time()
            
            self.reconstructed_data = np.squeeze(reconstructed_scan)
            self.reconstructed_data = (self.reconstructed_data - np.min(self.reconstructed_data)) / (np.max(self.reconstructed_data) - np.min(self.reconstructed_data))
            
            plt.imshow(self.reconstructed_data, cmap='gray')
            plt.title("Reconstructed MRI Slice")
            plt.axis("off")
            plt.show()
    
            self.statusLabel.setText(f"✅ Reconstruction completed in {end_time - start_time:.2f}s!")
            self.progressBar.setValue(100)
            self.saveButton.setEnabled(True)
        except Exception as e:
            self.statusLabel.setText(f"❌ Error: {str(e)}")
    
    def save_mri(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save MRI File", "", "PNG Image (*.png)")
        if file_path:
            cv2.imwrite(file_path, (self.reconstructed_data * 255).astype(np.uint8))
            self.statusLabel.setText("✅ MRI saved successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MRIReconstructionApp()
    ex.show()
    sys.exit(app.exec_())
