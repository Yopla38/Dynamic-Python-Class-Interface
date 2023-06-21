It's simple: I have a class called ProcessImage() without a graphical interface, and I want a graphical interface for testing or other purposes.

Just follow these steps:

1. Import the class:
```python
from Class_GUI_maker import DynamicConfigWindow
```

2. Create an instance of the configuration class you want to pass:
```python
config_class = ProcessImage()
```

3. Create and execute an instance of DynamicConfigWindow by passing the configuration instance and specifying the `execute_method` if necessary:
```python
# Use execute_method=True if you want to play with your class methods. Use False if you only want to change attributes.
window = DynamicConfigWindow(config_class, execute_method=True)
```

4. If you need to retrieve the modified configuration instance after the window is closed, do the following:
```python
modified_class = window.get_config()
print(modified_class)
```


## Typing attributes and method parameters

For the `DynamicConfigWindow` to work correctly with your class, it is important to annotate the data types of both attribute and method parameters in the class you want to edit. The GUI elements rendered by `DynamicConfigWindow` are based on the annotated data types to create the appropriate inputs for each data type.

Here is an example of a class with typed attributes and method parameters:

```python
class ProcessImage:
    some_boolean: bool = True
    an_integer: int = 42
    a_float: float = 3.14
    a_string: str = "Hello, world!"

    def example_method(self, lower: int, upper: int, message: str):
        # Your method implementation here...
```

The `DynamicConfigWindow` GUI will automatically adjust the displayed input fields for these data types, allowing you to configure them easily through the interface.
See the example_class.py for more...
