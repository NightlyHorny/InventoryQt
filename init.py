from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QHBoxLayout, QSplitter, QSizePolicy, QAbstractItemView, QHeaderView, QTextEdit, QListWidget, QListWidgetItem, QSpacerItem, QComboBox, QSpinBox, QMenu
from PyQt6.QtGui import QPixmap, QIcon, QAction
from PyQt6.QtCore import Qt, QSize  
import sys
import json
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Control de Inventario')
        self.setGeometry(100, 100, 1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Splitter to separate table and right layout
        self.splitter = QSplitter()
        self.main_layout.addWidget(self.splitter)

        # Table to display products
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Nombre', 'Unidades', 'Imagen'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.splitter.addWidget(self.table)

        # Right layout for image display and buttons
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to control spacing

        # Image display label with fixed size
        self.image_display_label = QLabel()
        self.image_display_label.setFixedSize(100, 100)  # Set size for image QLabel
        self.image_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(self.image_display_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Product selection combo box
        self.product_combo_box = QComboBox()
        self.right_layout.addWidget(self.product_combo_box)

        # Quantity selection spin box
        self.quantity_spin_box = QSpinBox()
        self.quantity_spin_box.setRange(0, 9999)  # Set range for quantity
        self.right_layout.addWidget(self.quantity_spin_box)

        # Button to add product and quantity to the list
        self.add_to_notes_button = QPushButton('Agregar a Notas')
        self.add_to_notes_button.clicked.connect(self.add_product_to_notes)
        self.right_layout.addWidget(self.add_to_notes_button)

        # List widget to display added products and quantities
        self.notes_list_widget = QListWidget()
        self.notes_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_list_widget.customContextMenuRequested.connect(self.show_list_widget_context_menu)
        self.right_layout.addWidget(self.notes_list_widget)

        # Notes area for additional details
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Notas adicionales...")
        self.right_layout.addWidget(self.notes_text)

        # Button to add a new product
        self.add_button = QPushButton('Agregar Producto')
        self.add_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Fixed size policy
        self.add_button.clicked.connect(self.add_product)
        self.right_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer to push the button to the bottom
        self.right_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Placeholder widget for the right layout
        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)
        self.splitter.addWidget(self.right_widget)

        # Initialize notes_data dictionary
        self.notes_data = {}

        # Load data automatically on startup
        self.load_from_json()

        # Connect table item selection change to update image and notes
        self.table.itemSelectionChanged.connect(self.update_image_and_notes_from_selection)

        # Set initial size of the first widget (table) to give more space
        self.splitter.setSizes([900, 100])  # First number is for the table, second for the right layout

        # Variable to keep track of the selected product
        self.selected_product_row = -1
        # Update the notes_list_widget
        self.update_notes_list_widget()

    def load_from_json(self):
        try:
            with open('product.json', 'r') as file:
                data = json.load(file)
                self.populate_table(data)
        except FileNotFoundError:
            print("File 'product.json' not found.")
            # Handle file not found error as needed

        # Load notes data and update table
        self.load_notes_from_json()
        self.load_additional_notes_from_json()  # Load additional notes
        self.update_table_with_notes()

    def load_notes_from_json(self):
        try:
            with open('unitsTable.json', 'r') as file:
                self.notes_data = json.load(file)
        except FileNotFoundError:
            self.notes_data = {}

    def load_additional_notes_from_json(self):
        try:
            with open('additionalNotes.json', 'r') as file:
                additional_notes = json.load(file)
                self.notes_text.setPlainText(additional_notes.get('additional_notes', ''))
        except FileNotFoundError:
            pass

    def save_to_json(self):
        data = self.collect_data_from_table()
        with open('product.json', 'w') as file:
            json.dump(data, file, indent=4)

    def save_notes_to_json(self):
        with open('unitsTable.json', 'w') as file:
            json.dump(self.notes_data, file, indent=4)

    def save_additional_notes_to_json(self):
        additional_notes = {'additional_notes': self.notes_text.toPlainText()}
        with open('additionalNotes.json', 'w') as file:
            json.dump(additional_notes, file, indent=4)

    def populate_table(self, data):
        self.table.setRowCount(len(data))
        for row, product in enumerate(data):
            nombre = product.get('nombre', '')
            unidades = product.get('unidades', 0)
            imagen = product.get('imagen', '')

            self.table.setItem(row, 0, QTableWidgetItem(nombre))
            self.table.setItem(row, 1, QTableWidgetItem(str(unidades)))

            # Set row height
            self.table.setRowHeight(row, 50)

            # Add button to change image
            change_image_button = QPushButton()
            change_image_button.setIcon(QIcon('images/change_icon.png'))
            change_image_button.setFixedSize(20, 20)  # Set button size
            change_image_button.setIconSize(QSize(20, 20))  # Adjust icon size to button size
            change_image_button.clicked.connect(lambda checked, row=row: self.select_image(row))

            # Create layout to hold the route and the button
            image_layout = QHBoxLayout()
            image_widget = QWidget()
            image_label = QLabel(imagen)
            image_layout.addWidget(image_label)

            # Spacer item to add space between image_label and change_image_button
            spacer_item = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            image_layout.addItem(spacer_item)

            image_layout.addWidget(change_image_button)
            image_widget.setLayout(image_layout)
            self.table.setCellWidget(row, 2, image_widget)

            # Add notes data
            if nombre in self.notes_data:
                item = self.table.item(row, 1)
                if item:
                    unidades_iniciales = int(item.text())
                    unidades_restantes = unidades_iniciales - self.notes_data[nombre]
                    self.table.item(row, 1).setText(str(unidades_restantes))

        # Populate product combo box with product names
        self.update_product_combo_box()

    def collect_data_from_table(self):
        data = []
        for row in range(self.table.rowCount()):
            nombre_item = self.table.item(row, 0)
            unidades_item = self.table.item(row, 1)
            ruta_widget = self.table.cellWidget(row, 2)

            if nombre_item and unidades_item and ruta_widget:
                nombre = nombre_item.text()
                unidades = unidades_item.text()
                ruta_layout = ruta_widget.layout() if ruta_widget else None
                ruta_label = ruta_layout.itemAt(0).widget() if ruta_layout and ruta_layout.itemAt(0) else None
                imagen = ruta_label.text() if isinstance(ruta_label, QLabel) else ''

                product = {
                    'nombre': nombre,
                    'unidades': unidades,
                    'imagen': imagen
                }
                data.append(product)

        return data

    def add_product(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem('Nuevo Producto'))
        self.table.setItem(row, 1, QTableWidgetItem('0'))

        change_image_button = QPushButton()
        change_image_button.setIcon(QIcon('images/change_icon.png'))
        change_image_button.setFixedSize(20, 20)  # Set button size
        change_image_button.setIconSize(QSize(20, 20))  # Adjust icon size to button size
        change_image_button.clicked.connect(lambda: self.select_image(row))

        image_layout = QHBoxLayout()
        image_widget = QWidget()
        image_label = QLabel()
        image_layout.addWidget(image_label)

        # Spacer item to add space between image_label and change_image_button
        spacer_item = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        image_layout.addItem(spacer_item)

        image_layout.addWidget(change_image_button)
        image_widget.setLayout(image_layout)
        self.table.setCellWidget(row, 2, image_widget)

        self.update_product_combo_box()

    def select_image(self, row):
        filename, _ = QFileDialog.getOpenFileName(self, 'Seleccionar imagen', '', 'Image files (*.jpg *.gif *.png)')
        if filename:
            image_label = self.table.cellWidget(row, 2).layout().itemAt(0).widget()
            image_label.setText(filename)

    def update_product_combo_box(self):
        self.product_combo_box.clear()
        for row in range(self.table.rowCount()):
            product_name = self.table.item(row, 0).text()
            self.product_combo_box.addItem(product_name)

    def update_image_and_notes_from_selection(self):
        selected_row = self.table.currentRow()
        if (selected_row >= 0):
            image_path = self.table.cellWidget(selected_row, 2).layout().itemAt(0).widget().text()
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                self.image_display_label.setPixmap(pixmap.scaled(self.image_display_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self.image_display_label.clear()

    def add_product_to_notes(self):
        product_name = self.product_combo_box.currentText()
        quantity = self.quantity_spin_box.value()
        note = self.notes_text.toPlainText()

        if product_name:
            self.notes_data[product_name] = self.notes_data.get(product_name, 0) + quantity
            self.update_notes_list_widget()

    def update_notes_list_widget(self):
        self.notes_list_widget.clear()
        for product_name, quantity in self.notes_data.items():
            item = QListWidgetItem(f"{product_name}: {quantity}")
            self.notes_list_widget.addItem(item)

        self.update_table_with_notes()

    def update_table_with_notes(self):
        quantity = self.quantity_spin_box.value()
        for row in range(self.table.rowCount()):
            product_name = self.table.item(row, 0).text()
            if product_name in self.notes_data:
                unidades_iniciales = int(self.table.item(row, 1).text())
                unidades_restantes = unidades_iniciales - quantity
                self.table.item(row, 1).setText(str(unidades_restantes))

    def show_list_widget_context_menu(self, position):
        menu = QMenu(self)
        remove_action = QAction('Eliminar', self)
        remove_action.triggered.connect(self.remove_selected_note)
        menu.addAction(remove_action)
        menu.exec(self.notes_list_widget.mapToGlobal(position))

    def remove_selected_note(self):
        selected_items = self.notes_list_widget.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            product_name = item.text().split(":")[0]
            quantity = int(item.text().split(":")[1])
            if product_name in self.notes_data:
                del self.notes_data[product_name]

                # Update units in the table
                for row in range(self.table.rowCount()):
                    if self.table.item(row, 0).text() == product_name:
                        unidades_restantes = int(self.table.item(row, 1).text()) + quantity
                        self.table.item(row, 1).setText(str(unidades_restantes))
                        break

        self.update_notes_list_widget()

    def closeEvent(self, event):
        self.save_to_json()
        self.save_notes_to_json()
        self.save_additional_notes_to_json()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
