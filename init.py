from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QHBoxLayout, QSplitter, QSizePolicy, QAbstractItemView, QHeaderView, QTextEdit, QListWidget, QListWidgetItem, QSpacerItem, QLineEdit, QComboBox, QSpinBox, QMenu
from PyQt6.QtGui import QPixmap, QIcon, QAction
from PyQt6.QtCore import Qt, QSize  
from shutil import copyfile
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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Nombre', 'Unidades', 'Imagen', 'Unidades Máximas'])
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
            with open('productos.json', 'r') as file:
                data = json.load(file)
                self.populate_table(data)
        except FileNotFoundError:
            print("File 'productos.json' not found.")
            # Handle file not found error as needed

        # Load notes data and update table
        self.load_notes_from_json()
        self.update_table_with_notes()

    def load_notes_from_json(self):
        try:
            with open('notas.json', 'r') as file:
                self.notes_data = json.load(file)
        except FileNotFoundError:
            self.notes_data = {}

    def save_to_json(self):
        data = self.collect_data_from_table()
        with open('productos.json', 'w') as file:
            json.dump(data, file, indent=4)

    def save_notes_to_json(self):
        with open('notas.json', 'w') as file:
            json.dump(self.notes_data, file, indent=4)

    def populate_table(self, data):
        self.table.setRowCount(len(data))
        for row, product in enumerate(data):
            nombre = product.get('nombre', '')
            unidades = product.get('unidades', 0)
            imagen = product.get('imagen', '')
            unidades_maximas = product.get('unidades_maximas', 0)

            self.table.setItem(row, 0, QTableWidgetItem(nombre))
            self.table.setItem(row, 1, QTableWidgetItem(str(unidades)))
            self.table.setItem(row, 3, QTableWidgetItem(str(unidades_maximas)))

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
            unidades_maximas_item = self.table.item(row, 3)

            if nombre_item and unidades_item and ruta_widget and unidades_maximas_item:
                nombre = nombre_item.text()
                unidades = unidades_item.text()
                ruta_layout = ruta_widget.layout() if ruta_widget else None
                ruta_label = ruta_layout.itemAt(0).widget() if ruta_layout and ruta_layout.itemAt(0) else None
                imagen = ruta_label.text() if isinstance(ruta_label, QLabel) else ''
                unidades_maximas = unidades_maximas_item.text()

                # Check if unidades exceed unidades_maximas
                if int(unidades) > int(unidades_maximas):
                    unidades = unidades_maximas_item.text()

                product = {
                    'nombre': nombre,
                    'unidades': unidades,
                    'imagen': imagen,
                    'unidades_maximas': unidades_maximas
                }
                data.append(product)

        return data

    def add_product(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem('Nuevo Producto'))
        self.table.setItem(row, 1, QTableWidgetItem('0'))
        self.table.setItem(row, 3, QTableWidgetItem('0'))

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
        filename, _ = QFileDialog.getOpenFileName(self, 'Seleccionar Imagen', '', 'Archivos de Imagen (*.jpg *.png)')
        if filename:
            # Show selected image in QLabel
            pixmap = QPixmap(filename)
            pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_display_label.setPixmap(pixmap)
            self.image_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Update image path in the table cell widget
            image_widget = self.table.cellWidget(row, 2)
            image_label = image_widget.layout().itemAt(0).widget() if image_widget else None
            if image_label and isinstance(image_label, QLabel):
                image_label.setText(filename)  # Update the QLabel with the new image path
            else:
                # Create a new label if none exists
                image_label = QLabel(filename)
                image_layout = QHBoxLayout()
                image_layout.addWidget(image_label)

                # Spacer item to add space between image_label and change_image_button
                spacer_item = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                image_layout.addItem(spacer_item)

                # Recreate change_image_button
                change_image_button = QPushButton()
                change_image_button.setIcon(QIcon('images/change_icon.png'))
                change_image_button.setFixedSize(20, 20)  # Set button size
                change_image_button.setIconSize(QSize(20, 20))  # Adjust icon size to button size
                change_image_button.clicked.connect(lambda checked, row=row: self.select_image(row))
                image_layout.addWidget(change_image_button)

                image_widget.setLayout(image_layout)
                self.table.setCellWidget(row, 2, image_widget)

            # Guardar la imagen en la carpeta images
            basename = os.path.basename(filename)
            self.table.cellWidget(row, 2).layout().itemAt(0).widget().setText(f"images/{basename}")
            copyfile(filename, f"images/{basename}")

    def add_product_to_notes(self):
        product_name = self.product_combo_box.currentText()
        quantity = self.quantity_spin_box.value()

        # Find the corresponding row in the table
        product_row = None
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == product_name:
                product_row = row
                break

        if product_row is not None:
            unidades_item = self.table.item(product_row, 1)
            unidades_maximas_item = self.table.item(product_row, 3)

            if unidades_item and unidades_maximas_item:
                unidades_disponibles = int(unidades_item.text())
                unidades_maximas = int(unidades_maximas_item.text())

                if quantity <= unidades_disponibles and quantity <= unidades_maximas:
                    # Update or add product in notes_data
                    if product_name in self.notes_data:
                        if self.notes_data[product_name] + quantity <= unidades_maximas:
                            self.notes_data[product_name] += quantity
                        else:
                            self.notes_data[product_name] = unidades_maximas
                    else:
                        self.notes_data[product_name] = min(quantity, unidades_maximas)

                    # Update the notes_list_widget
                    self.update_notes_list_widget()

                    # Update table with remaining quantities
                    self.update_table_with_notes()

                else:
                    print(f"La cantidad total no puede exceder las unidades disponibles ({unidades_disponibles}) ni las unidades máximas ({unidades_maximas}).")
            else:
                print("No se pudo encontrar las unidades disponibles o máximas.")
        else:
            print("No se pudo encontrar el producto en la tabla.")

    def update_notes_list_widget(self):
        self.notes_list_widget.clear()
        for product, quantity in self.notes_data.items():
            item = QListWidgetItem(f"{product}: {quantity}")
            self.notes_list_widget.addItem(item)

        # Save notes data to JSON file
        self.save_notes_to_json()

    def update_image_and_notes_from_selection(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            # Update image display
            row = selected_items[0].row()
            ruta_widget = self.table.cellWidget(row, 2)
            ruta_layout = ruta_widget.layout() if ruta_widget else None
            ruta_label = ruta_layout.itemAt(0).widget() if ruta_layout and ruta_layout.itemAt(0) else None
            image_path = ruta_label.text() if isinstance(ruta_label, QLabel) else ''

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_display_label.setPixmap(pixmap)
                self.image_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_product_combo_box(self):
        self.product_combo_box.clear()
        for row in range(self.table.rowCount()):
            nombre_item = self.table.item(row, 0)
            if nombre_item:
                self.product_combo_box.addItem(nombre_item.text())

    def update_table_with_notes(self):
        for row in range(self.table.rowCount()):
            nombre_item = self.table.item(row, 0)
            unidades_item = self.table.item(row, 1)
            unidades_maximas_item = self.table.item(row, 3)

            if nombre_item and unidades_item and unidades_maximas_item:
                nombre = nombre_item.text()
                unidades_iniciales = int(unidades_item.text())
                unidades_maximas = int(unidades_maximas_item.text())

                if nombre in self.notes_data:
                    quantity_in_notes = self.notes_data[nombre]
                    unidades_restantes = unidades_iniciales - quantity_in_notes
                    if unidades_restantes > unidades_maximas:
                        unidades_restantes = unidades_maximas
                    self.table.item(row, 1).setText(str(unidades_restantes))
                else:
                    self.table.item(row, 1).setText(str(unidades_iniciales))

    def closeEvent(self, event):
        # Save data to JSON files before closing
        self.save_to_json()
        self.save_notes_to_json()
        event.accept()

    def show_list_widget_context_menu(self, position):
        menu = QMenu()
        delete_action = QAction('Eliminar', self)
        delete_action.triggered.connect(self.delete_selected_note)
        menu.addAction(delete_action)
        menu.exec(self.notes_list_widget.viewport().mapToGlobal(position))

    def delete_selected_note(self):
        selected_items = self.notes_list_widget.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            product_info = item.text().split(':')
            product_name = product_info[0].strip()
            quantity = int(product_info[1].strip())

            # Remove item from QListWidget
            self.notes_list_widget.takeItem(self.notes_list_widget.row(item))

            # Remove from notes_data
            if product_name in self.notes_data:
                del self.notes_data[product_name]

            # Update table with restored quantities
            for row in range(self.table.rowCount()):
                nombre_item = self.table.item(row, 0)
                unidades_item = self.table.item(row, 1)
                unidades_maximas_item = self.table.item(row, 3)

                if nombre_item and unidades_item and unidades_maximas_item:
                    nombre = nombre_item.text()
                    if nombre == product_name:
                        unidades_iniciales = int(unidades_item.text())
                        unidades_maximas = int(unidades_maximas_item.text())
                        unidades_restantes = min(unidades_iniciales + quantity, unidades_maximas)
                        self.table.item(row, 1).setText(str(unidades_restantes))

        # Save notes data to JSON file
        self.save_notes_to_json()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
