"""Detect Throws Exception Static and Dynamic Analysis Tool."""

import ast
import subprocess
import sys
import tempfile
import os

class DetectThrowsException:
    def __init__(self, file_path: str):
        """Initialize with path to the Python file we want to analyze."""
        self.file_path = file_path
        try:
            with open(file_path, 'r') as f:
                self.source = f.read()
        except Exception as e:
            self.source = ""
            self.file_error = e
            self.tree = None
            self.findings = [("file-error", f"Error reading file: {str(e)}")]
            return
            
        try:
            self.tree = ast.parse(self.source)
        except SyntaxError as e:
            self.tree = None
            self.syntax_error = e
        self.findings = []
    
    def syntactic_checks(self):
        """Find definite 'raise' statements and literal division-by-zero."""
        if self.tree is None:
            self.findings.append(("syntax-error", f"Syntax error in code: {getattr(self, 'syntax_error', 'Unknown syntax error')}"))
            return
            
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Raise):
                # Found explicit raise
                self.findings.append(("definite-raise", f"explicit raise at line {node.lineno}"))
            # look for binary division with literal 0 on right
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv)):
                right = node.right
                if isinstance(right, ast.Constant) and right.value == 0:
                    self.findings.append(("definite-div-zero", f"division by literal 0 at line {node.lineno}"))
            # look for integer literal modulo 0 as well
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                right = node.right
                if isinstance(right, ast.Constant) and right.value == 0:
                    self.findings.append(("definite-mod-zero", f"modulo by literal 0 at line {node.lineno}"))
    
    def dynamic_run(self, timeout=30):
        """Run the Python file dynamically using subprocess and detect if it throws exceptions."""
        try:
            result = subprocess.run(
                [sys.executable, self.file_path], 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode != 0:
                return {
                    "threw": True,
                    "exc_info": result.stderr.strip(),
                    "timed_out": False,
                    "stdout": result.stdout.strip()
                }
            else:
                return {
                    "threw": False,
                    "exc_info": None,
                    "timed_out": False,
                    "stdout": result.stdout.strip()
                }
                
        except subprocess.TimeoutExpired:
            return {
                "threw": True,
                "exc_info": f"Timeout after {timeout}s (possible infinite loop or hanging)",
                "timed_out": True,
                "stdout": ""
            }
        except Exception as e:
            return {
                "threw": True,
                "exc_info": f"Error running file: {str(e)}",
                "timed_out": False,
                "stdout": ""
            }
    
    def analyze(self, run_timeout=30):
        """Perform combined static and dynamic analysis. Always runs both."""
        self.findings = []
        self.syntactic_checks()
        dynamic = self.dynamic_run(timeout=run_timeout)
        return {"static_findings": self.findings, "dynamic_result": dynamic}

# Demonstration
if __name__ == "__main__":
    # Test cases demonstrating the static + dynamic approach
    # call them here
