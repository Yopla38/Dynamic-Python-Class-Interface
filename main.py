# Créer une instance de la classe de configuration que vous souhaitez passer
from Class_GUI_maker import DynamicConfigWindow
from example_class import ProcessImage


if __name__ == "__main__":
    # Create an instance of the configuration class you want to pass
    config_class = ProcessImage()

    # Create and execute an instance of DynamicConfigWindow by passing the configuration instance and execute_method if necessary
    window = DynamicConfigWindow(config_class, execute_method=True)

    # If you need to retrieve the modified configuration instance after window closure
    modified_class = window.get_config()
    print(modified_class)

'''
In this example, we create an instance of the `ProcessImage` class (which you should replace with your desired 
configuration class) and pass this instance to the `DynamicConfigWindow` class. If no QApplication exists, 
a new QApplication will be created, and the window will display and execute automatically. You can also retrieve the 
modified configuration instance after the window closes using the `get_config()` method.
'''