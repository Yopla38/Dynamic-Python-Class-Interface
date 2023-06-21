# Copyright CEA Grenoble 2023
# Auteur : Yoann CURE
# MIT Licence

import copy
import os
import sys
from functools import partial
from inspect import signature, Parameter

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QWidget, QCheckBox, QSpinBox, QLabel, QDoubleSpinBox, \
    QLineEdit, QComboBox, QApplication, QHBoxLayout, QPushButton, QFileDialog, QWidgetItem

from example_class import ProcessImage


class DynamicConfigWindow(QDialog):
    app_initiated = False  # Variable de classe pour suivre si l'application a été initiée

    def __init__(self, config_class, execute_method: bool = True):
        # Vérifier s'il existe déjà une QApplication
        app = QCoreApplication.instance()

        # Créer une nouvelle QApplication si aucune n'existe et si aucune n'a été initiée auparavant
        if app is None and not DynamicConfigWindow.app_initiated:
            app = QApplication(sys.argv)
            DynamicConfigWindow.app_initiated = True

        super().__init__()
        self.modified_config = None
        self.config_class = config_class  # ajout de l'attribut config_class

        self.original_config = copy.deepcopy(config_class) if not execute_method else None

        self.setWindowTitle("Class GUI maker")

        # Configuration de la disposition principale
        main_layout = QVBoxLayout(self)

        # Création de la zone de scroll
        scroll = QScrollArea()
        main_layout.addWidget(scroll)

        # Création du contenu de la zone de scroll
        scroll_content = QWidget()
        scroll_content.setLayout(QVBoxLayout())
        scroll.setWidget(scroll_content)

        # Ajoutez un QLabel pour séparer les attributs de la classe
        attributes_title = QLabel("Attributes")
        attributes_title.setStyleSheet("font-weight: bold;")
        scroll_content.layout().addWidget(attributes_title)

        self.config = config_class

        for attr_name, attr_type in self.config.__annotations__.items():

            # Exclure les attributs spéciaux et méthodes
            if not attr_name.startswith("__") and not callable(getattr(self.config, attr_name)) and attr_name in self.config.__annotations__:
                attr_value = getattr(self.config, attr_name)

                if attr_type is bool:
                    # Création d'une QCheckBox pour les booléens
                    checkbox = QCheckBox(attr_name)
                    checkbox.setChecked(attr_value)
                    checkbox.stateChanged.connect(lambda state, attr_name=attr_name: setattr(self.config, attr_name, state == 2))
                    scroll_content.layout().addWidget(checkbox)

                elif attr_type is int:
                    # Création d'une QSpinBox pour les entiers
                    spinbox = QSpinBox()
                    spinbox.setMinimum(-2147483648)
                    spinbox.setMaximum(2147483647)
                    spinbox.setSingleStep(1)
                    spinbox.setValue(attr_value)
                    spinbox.valueChanged.connect(lambda value, attr_name=attr_name: setattr(self.config, attr_name, value))
                    scroll_content.layout().addWidget(QLabel(attr_name))
                    scroll_content.layout().addWidget(spinbox)

                elif attr_type is float:
                    # Création d'une QDoubleSpinBox pour les flottants
                    spinbox = QDoubleSpinBox()
                    spinbox.setMinimum(-sys.float_info.max)
                    spinbox.setMaximum(sys.float_info.max)
                    spinbox.setSingleStep(0.1)
                    spinbox.setValue(attr_value)
                    spinbox.valueChanged.connect(lambda value, attr_name=attr_name: setattr(self.config, attr_name, value))
                    scroll_content.layout().addWidget(QLabel(attr_name))
                    scroll_content.layout().addWidget(spinbox)

                elif attr_type is str:
                    # Création d'un QLineEdit pour les chaînes de caractères
                    line_edit = QLineEdit(attr_value)
                    line_edit.textChanged.connect(lambda value, attr_name=attr_name: setattr(self.config, attr_name, value))
                    scroll_content.layout().addWidget(QLabel(attr_name))
                    scroll_content.layout().addWidget(line_edit)

                elif isinstance(attr_value, (list, tuple)):
                    # Création d'un QComboBox pour les listes et tuples
                    combo_box = QComboBox()
                    combo_box.setEditable(True)
                    combo_box.addItems([str(i) for i in attr_value])

                    # Connexion du signal editingFinished() pour mettre à jour l'élément sélectionné
                    combo_box.lineEdit().editingFinished.connect(lambda c=combo_box: update_current_item(c))

                    # Mise à jour de la connexion du signal currentTextChanged
                    combo_box.currentTextChanged.connect(
                        lambda value, attr_name=attr_name, c=combo_box: setattr(self.config, attr_name, str_to_list(
                            value)) if c.hasFocus() else None)

                    # Création d'un QHBoxLayout pour les boutons Ajouter et Supprimer
                    buttons_layout = QHBoxLayout()

                    # Création du bouton Ajouter
                    add_button = QPushButton("+")
                    add_button.clicked.connect(lambda _,
                                c=combo_box: (c.insertItem(c.currentIndex() + 1, ""),
                                c.setCurrentIndex(c.currentIndex() + 1)) if c.currentIndex() + 1 < c.count() else c.addItem(""))
                    buttons_layout.addWidget(add_button)

                    # Création du bouton Supprimer
                    remove_button = QPushButton("-")
                    remove_button.clicked.connect(
                        lambda _, c=combo_box: c.removeItem(c.currentIndex()) if c.currentIndex() >= 0 else None)
                    buttons_layout.addWidget(remove_button)

                    # Ajout des widgets au layout principal
                    scroll_content.layout().addWidget(QLabel(attr_name))
                    scroll_content.layout().addWidget(combo_box)
                    scroll_content.layout().addLayout(buttons_layout)

                elif attr_type is 'filepath' or attr_type is os.path:
                    # Créez un QLabel pour l'attribut
                    label = QLabel(attr_name)

                    # Créez un QLineEdit pour l'attribut
                    line_edit = QLineEdit(attr_value)

                    # Créez un QPushButton pour ouvrir un QFileDialog
                    file_dialog_button = QPushButton("Browse")
                    file_dialog_button.clicked.connect(partial(self.open_file_dialog, line_edit))

                    # Créez un QHBoxLayout pour le QLineEdit et le QPushButton
                    hbox_layout = QHBoxLayout()
                    hbox_layout.addWidget(line_edit)
                    hbox_layout.addWidget(file_dialog_button)

                    # Connexion du signal pour mettre à jour l'attribut
                    line_edit.textChanged.connect(
                        lambda value, attr_name=attr_name: setattr(self.config, attr_name, value))

                    # Ajoutez le QLabel et le QHBoxLayout au layout
                    scroll_content.layout().addWidget(label)
                    scroll_content.layout().addLayout(hbox_layout)

                elif issubclass(attr_type, object):  # Vérifiez si attr_type est une classe
                    # Création d'un QLabel pour l'attribut
                    label = QLabel(attr_name)

                    # Création d'un QPushButton pour ouvrir une nouvelle instance de DynamicConfigWindow
                    config_button = QPushButton("Configure")
                    config_button.clicked.connect(
                        lambda _, attr_name=attr_name, attr_type=attr_type: self.open_dynamic_config_window(attr_name,
                                                                                                            attr_type))

                    # Création d'un QHBoxLayout pour le QLabel et le QPushButton
                    hbox_layout = QHBoxLayout()
                    hbox_layout.addWidget(label)
                    hbox_layout.addWidget(config_button)

                    # Ajout du QHBoxLayout au layout principal
                    scroll_content.layout().addLayout(hbox_layout)

        if execute_method:
            # Ajoutez un QLabel pour séparer les méthodes
            methods_title = QLabel("Methods")
            methods_title.setStyleSheet("font-weight: bold;")
            scroll_content.layout().addWidget(methods_title)


            # Ajoutez une QComboBox pour afficher les méthodes publiques
            self.methods_combo_box = QComboBox()
            # Ajoutez la QComboBox pour les méthodes sous le QLabel "Methods"
            scroll_content.layout().addWidget(self.methods_combo_box)
            method_names = [attr_name for attr_name in dir(self.config) if
                            callable(getattr(self.config, attr_name)) and not attr_name.startswith("__")]

            self.methods_combo_box.addItems(method_names)
            self.methods_combo_box.currentIndexChanged.connect(self.update_method_params)

            # Ajoutez un QLabel pour séparer les paramètres des méthodes
            params_title = QLabel("Parameters")
            params_title.setStyleSheet("font-weight: bold;")
            scroll_content.layout().addWidget(params_title)
            # Créez un conteneur pour les widgets des paramètres d'entrée
            self.param_widgets_container = QWidget()
            self.param_widgets_container.setLayout(QVBoxLayout())
            scroll_content.layout().addWidget(self.param_widgets_container)

            # Ajoutez un QPushButton pour exécuter la méthode sélectionnée
            self.run_button = QPushButton("Run method")
            self.run_button.clicked.connect(self.run_method)

            main_layout.addWidget(self.run_button)
            self.update_method_params()

        # Ajout des boutons Ok et Cancel
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Ok")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        # Connexion des signaux pour les boutons Ok et Cancel
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        scroll.setWidgetResizable(True)

        # Afficher et exécuter le widget
        self.show()
        if app is not None:
            self.exec()
    def open_dynamic_config_window(self, attr_name, attr_type):
        # Obtenir l'attribut actuel
        current_attr = getattr(self.config, attr_name)

        # Créer une nouvelle instance de DynamicConfigWindow avec le type de l'attribut
        sub_config_window = DynamicConfigWindow(current_attr if current_attr else attr_type(), execute_method=False)
        result = sub_config_window.exec()

        if result == QDialog.DialogCode.Accepted:
            # Mettre à jour l'attribut dans self.config_class
            setattr(self.config, attr_name, sub_config_window.get_config())

            # Mettre à jour l'attribut dans self.config_class
            setattr(self.config_class, attr_name, sub_config_window.get_config())
    def update_method_params(self):
        # Effacez les anciens widgets de paramètres d'entrée
        for i in range(self.param_widgets_container.layout().count()):
            self.param_widgets_container.layout().takeAt(0).widget().deleteLater()

        # Obtenez la méthode sélectionnée et sa signature
        method_name = self.methods_combo_box.currentText()
        method = getattr(self.config, method_name, None)
        if not method:
            return

        method_signature = signature(method)
        params = method_signature.parameters

        for param_name, param in params.items():
            # Créer et ajouter des widgets en fonction des types de paramètres d'entrée
            param_type = param.annotation if param.annotation != Parameter.empty else type(param.default)

            if param_type is str:

                # Créez un QLabel pour le paramètre
                label = QLabel(param_name)

                # Créez un QLineEdit pour le paramètre
                line_edit = QLineEdit(param.default if param.default != Parameter.empty else '')

                # Ajoutez le QLabel et le QLineEdit au layout
                self.param_widgets_container.layout().addWidget(label)
                self.param_widgets_container.layout().addWidget(line_edit)
            elif param_type is bool:
                # Créez un QLabel pour le paramètre
                label = QLabel(param_name)

                # Créez un QCheckBox pour le paramètre
                checkbox = QCheckBox()
                checkbox.setChecked(param.default if param.default != Parameter.empty else False)

                # Ajoutez le QLabel et le QCheckBox au layout
                self.param_widgets_container.layout().addWidget(label)
                self.param_widgets_container.layout().addWidget(checkbox)

            elif param_type is int:
                # Créez un QLabel pour le paramètre
                label = QLabel(param_name)

                # Créez un QSpinBox pour le paramètre
                spinbox = QSpinBox()
                spinbox.setMinimum(-2147483648)
                spinbox.setMaximum(2147483647)
                spinbox.setSingleStep(1)
                spinbox.setValue(param.default if param.default != Parameter.empty else 0)

                # Ajoutez le QLabel et le QSpinBox au layout
                self.param_widgets_container.layout().addWidget(label)
                self.param_widgets_container.layout().addWidget(spinbox)

            elif param_type is float:
                # Créez un QLabel pour le paramètre
                label = QLabel(param_name)

                # Créez un QDoubleSpinBox pour le paramètre
                spinbox = QDoubleSpinBox()
                spinbox.setMinimum(-sys.float_info.max)
                spinbox.setMaximum(sys.float_info.max)
                spinbox.setSingleStep(0.1)
                spinbox.setValue(param.default if param.default != Parameter.empty else 0.0)

                # Ajoutez le QLabel et le QDoubleSpinBox au layout
                self.param_widgets_container.layout().addWidget(label)
                self.param_widgets_container.layout().addWidget(spinbox)

            elif param_type is 'filepath' or param_type is os.path:
                # Créez un QLabel pour le paramètre
                label = QLabel(param_name)

                # Créez un QLineEdit pour le paramètre
                line_edit = QLineEdit(param.default if param.default != Parameter.empty else "")

                # Créez un QPushButton pour ouvrir un QFileDialog
                file_dialog_button = QPushButton("Browse")
                file_dialog_button.clicked.connect(partial(self.open_file_dialog, line_edit))

                # Créez un QHBoxLayout pour le QLineEdit et le QPushButton
                hbox_layout = QHBoxLayout()
                hbox_layout.addWidget(line_edit)
                hbox_layout.addWidget(file_dialog_button)

                # Ajoutez le QLabel et le QHBoxLayout au layout
                self.param_widgets_container.layout().addWidget(label)
                self.param_widgets_container.layout().addLayout(hbox_layout)


    def open_file_dialog(self, line_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_name:
            line_edit.setText(file_name)

    def run_method(self):
        # Obtenez la méthode sélectionnée
        method_name = self.methods_combo_box.currentText()
        method = getattr(self.config, method_name, None)
        if not method:
            return

        # Obtenez les paramètres de la méthode et leurs widgets
        method_signature = signature(method)
        params = method_signature.parameters
        param_widgets = self.get_param_widgets()

        # Récupérez les valeurs des widgets de paramètres et convertissez-les en leurs types appropriés
        args = []
        for param_name, param in params.items():
            param_type = param.annotation if param.annotation != Parameter.empty else type(param.default)
            widget = param_widgets[param_name]
            widget_value = widget.text() if isinstance(widget, QLineEdit) else (
                widget.isChecked() if isinstance(widget, QCheckBox) else widget.value())

            # Convertir les valeurs en leur type approprié
            if param_type is str:
                converted_value = widget_value
            elif param_type is bool:
                converted_value = widget_value
            elif param_type is int:
                converted_value = int(widget_value)
            elif param_type is float:
                converted_value = float(widget_value)
            elif param_type is 'filepath' or param_type is os.path:
                converted_value = widget_value
            else:
                converted_value = None
                print("Value conversion error")
            args.append(converted_value)

        # Exécutez la méthode avec les arguments récupérés et convertis
        method(*args)

    def get_param_widgets(self):
        # Obtenez les widgets associés aux paramètres de la méthode
        param_widgets = {}
        for i in range(0, self.param_widgets_container.layout().count(), 2):
            param_name = self.param_widgets_container.layout().itemAt(i).widget().text()

            # Récupérer le widget d'entrée correct pour chaque type de widget
            widget_item = self.param_widgets_container.layout().itemAt(i + 1)
            if isinstance(widget_item, QWidgetItem):  # Vérifiez si l'objet est un widget
                input_widget = widget_item.widget()
            else:  # Sinon, il devrait être un layout
                widget_layout = widget_item.layout()
                input_widget = widget_layout.itemAt(0).widget()  # Utiliser le 1er élément du QHBoxLayout

            param_widgets[param_name] = input_widget

        return param_widgets

    def accept(self):
        # récupération de l'instance de config_class avec les valeurs modifiées
        modified_config = self.config_class
        for attr_name in dir(modified_config):
            if not attr_name.startswith("__") and not callable(getattr(modified_config, attr_name)):
                setattr(modified_config, attr_name, getattr(self.config_class, attr_name))
        self.modified_config = modified_config

        # Appel de la méthode QDialog accept()
        super().accept()

    def reject(self):
        self.modified_config = self.original_config if self.original_config is not None else None
        # Appel de la méthode QDialog reject()
        super().reject()

    def get_config(self):
        return self.modified_config


def update_current_item(combo_box):
    current_index = combo_box.currentIndex()
    current_text = combo_box.lineEdit().text()

    # Mise à jour de l'élément dans la liste
    if current_index >= 0:
        combo_box.setItemText(current_index, current_text)

def str_to_list(value):
    return [x.strip() for x in value.split(',')]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    config_class = ProcessImage()

    # Instanciation de la fenêtre de configuration dynamique
    window = DynamicConfigWindow(config_class, execute_method=True)
    window.show()
    result = window.exec()

    # récupération de l'instance modifiée après la fermeture de la fenêtre
    modified_class = window.get_config()
