# `detectThrowsException` Presentation

## Why is Exception Handling Difficult?

Exception handling is the process of managing unexpected events (exceptions) occuring during a program's execution. It is a common practice to prevent the program from unexpected crashes. While it is a good way of storing code segments that can cause crashes, but writing efficient exception handling in a codebase is hard since we have to know the outcome of a code segment before we execute it that can lead to crashes. It is kind of predicting the future problem and because of that exception handling can be quite difficult.

On the other hand we have static analysis which can help in detecting bugs, vulnerabilites or even code smells that could lead to crashes. It is important to note that static analysis does not replace exception handling!

## Example Exception Handling that Does Not Catch Exception(s)

While implementing exception handling we can face many difficulties. For example, writing exception handling does not guarantee that it will catch a method or function that we want to treat in a exceptional way. So even though our program has exception handling, it's not a guarantee that it will catch exception(s).

The following code example demonstrates a good example when the exception handling is used at the wrong place:

```python
class NoExcept:
    def __init__(self, file):
        self.file = file

    def openFile(self):
        """Opening file."""
        with open(self.file, "r") as fn:
            try:
                fn.read()
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Could not open {self.file}") from e
```

## Detect Throws Exception Static and Dynamic Analysis Tool

- Provides basic analysis for Python files to detect potential exceptions through two approaches:
  - Static analysis (AST-based)
  - Dynamic analysis (execution-based)

- Capabilities include:
  - Identifying explicit raise statements
  - Detecting division by zero operations
  - Finding runtime exceptions that may occur during program execution

```bash
uv run main.py
```

## Advantages Over Previous Approaches

- Combines both static and dynamic analysis methods
- Goes beyond simple pattern matching (checking for except blocks via regex)
- Executes code to detect real exception scenarios
- Provides more accurate detection of potential exception conditions

## Limitations

- Dynamic analysis requires code execution, which may not be safe for all code
- Cannot predict all possible runtime exceptions without comprehensive test cases
- Static analysis may miss exceptions from external dependencies or libraries
- Performance overhead when analyzing large codebases
