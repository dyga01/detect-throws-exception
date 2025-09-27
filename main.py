"""Detect Throws Exception Static and Dynamic Analysis Tool.

This module provides a comprehensive tool for analyzing Python files to detect
potential exceptions through both static (AST-based) and dynamic (execution-based)
analysis. It can identify explicit raise statements, division by zero operations,
and runtime exceptions.
"""

import ast
import subprocess
import sys

class DetectThrowsException:
    """A tool for detecting potential exceptions in Python files.
    
    Attributes:
        file_path (str): Path to the Python file being analyzed.
        source (str): Source code content of the file.
        tree (ast.AST): Abstract Syntax Tree of the parsed source code.
        findings (list): List of tuples containing static analysis findings.
        file_error (Exception): Any error encountered while reading the file.
        syntax_error (SyntaxError): Any syntax error encountered while parsing.
    """
    
    def __init__(self, file_path: str):
        """Initialize the analyzer with a Python file to analyze.
        
        Args:
            file_path (str): Path to the Python file to be analyzed.
        """
        self.file_path = file_path
        
        # Attempt to read the source file
        try:
            with open(file_path, 'r') as f:
                self.source = f.read()
        except Exception as e:
            # Handle file reading errors gracefully
            self.source = ""
            self.file_error = e
            self.tree = None
            self.findings = [("file-error", f"Error reading file: {str(e)}")]
            return
            
        # Attempt to parse the source code into an AST
        try:
            self.tree = ast.parse(self.source)
        except SyntaxError as e:
            # Handle syntax errors in the source code
            self.tree = None
            self.syntax_error = e
        
        # Initialize findings list for static analysis results
        self.findings = []
    
    def syntactic_checks(self):
        """Perform static analysis to find definite exception scenarios.
        
        This method uses AST (Abstract Syntax Tree) analysis to identify patterns
        in the code that will definitely cause exceptions, including:
        - Explicit raise statements
        - Division by literal zero
        - Modulo by literal zero
        
        The findings are stored in self.findings as tuples of (type, description).
        """
        # Check if we have a valid AST to analyze
        if self.tree is None:
            self.findings.append(("syntax-error", f"Syntax error in code: {getattr(self, 'syntax_error', 'Unknown syntax error')}"))
            return
        
        # Walk through all nodes in the Abstract Syntax Tree
        for node in ast.walk(self.tree):
            # Check for explicit raise statements
            if isinstance(node, ast.Raise):
                self.findings.append((
                    "definite-raise", 
                    f"explicit raise at line {node.lineno}"
                ))
            
            # Check for division operations that might cause ZeroDivisionError
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv)):
                right = node.right
                if isinstance(right, ast.Constant) and right.value == 0:
                    self.findings.append((
                        "definite-div-zero", 
                        f"division by literal 0 at line {node.lineno}"
                    ))
            
            # Check for modulo operations that might cause ZeroDivisionError
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                right = node.right
                if isinstance(right, ast.Constant) and right.value == 0:
                    self.findings.append((
                        "definite-mod-zero", 
                        f"modulo by literal 0 at line {node.lineno}"
                    ))
    
    def dynamic_run(self, timeout=30):
        """Execute the Python file and detect runtime exceptions.
        
        This method performs dynamic analysis by actually running the Python file
        in a subprocess and monitoring for exceptions or timeouts. This complements
        static analysis by catching runtime errors that may not be detectable
        through code inspection alone.
        """
        try:
            # Execute the Python file in a separate subprocess
            result = subprocess.run(
                [sys.executable, self.file_path],  # Use same Python interpreter
                capture_output=True,  # Capture both stdout and stderr
                text=True,           # Return strings instead of bytes
                timeout=timeout      # Kill process if it runs too long
            )
            
            # Non-zero exit code indicates an exception or error
            if result.returncode != 0:
                return {
                    "threw": True,
                    "exc_info": result.stderr.strip(),
                    "timed_out": False,
                    "stdout": result.stdout.strip()
                }
            # Zero exit code indicates successful execution
            else:
                return {
                    "threw": False,
                    "exc_info": None,
                    "timed_out": False,
                    "stdout": result.stdout.strip()
                }
        # Handle case where execution exceeds the timeout limit        
        except subprocess.TimeoutExpired:
            return {
                "threw": True,
                "exc_info": f"Timeout after {timeout}s (possible infinite loop or hanging)",
                "timed_out": True,
                "stdout": ""
            }
        # Handle any other errors that occur during subprocess execution
        except Exception as e:
            return {
                "threw": True,
                "exc_info": f"Error running file: {str(e)}",
                "timed_out": False,
                "stdout": ""
            }
    
    def analyze(self, run_timeout=30):
        """Perform comprehensive analysis combining static and dynamic approaches."""
        self.findings = []
        self.syntactic_checks()
        dynamic = self.dynamic_run(timeout=run_timeout)
        # Return combined results from both analysis approaches
        return {
            "static_findings": self.findings, 
            "dynamic_result": dynamic
        }

if __name__ == "__main__":
    """Example usage of the DetectThrowsException tool."""
    # Divide by zero test case
    test_file = "test_files/divide_by_zero.py"
    analyzer = DetectThrowsException(test_file)
    result = analyzer.analyze()
    print(f"Analysis results for {test_file}:")
    print(f"Static findings: {result['static_findings']}")
    print(f"Dynamic result: {result['dynamic_result']}")
