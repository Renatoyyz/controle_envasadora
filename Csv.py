import utime
import os
from maeda.SystemFile import File

class Csv:
    def __init__(self, labels = [], directory = "data.csv"):
        self.labels = labels
        self.file = File(directory)
        self._config()
        
    def _config(self):
        if not self.file.check_file():
            for i in range(0, len(self.labels)):
                if i < len(self.labels) - 1:
                    self.file.write_file_append(self.labels[i] + ";")
                else:
                    self.file.write_file_append(self.labels[i] + "\n")
                    
    def save_value(self, data = []):
        for i in range(0, len(data)):
            if i < len(data) - 1:
                self.file.write_file_append(data[i] + ";")
            else:
                self.file.write_file_append(data[i] + "\n")
    
    def update_value(self, row, column, new_value):
        lines = self.file.read_file().splitlines()
        if row < 1 or row >= len(lines):
            raise IndexError("Row out of range")
        columns = lines[row].split(";")
        if column < 0 or column >= len(columns):
            raise IndexError("Column out of range")
        columns[column] = new_value
        lines[row] = ";".join(columns)
        self.file.write_file("\n".join(lines) + "\n")
    
    def get_value(self, row, column):
        lines = self.file.read_file().splitlines()
        if row < 1 or row >= len(lines):
            raise IndexError("Row out of range")
        columns = lines[row].split(";")
        if column < 0 or column >= len(columns):
            raise IndexError("Column out of range")
        return columns[column]
            
if __name__ == "__main__":
    contador = 1234
    test = Csv(labels=['contador'])
    test.save_value([f"{contador}"])
    
    # Obtendo um valor
    value = test.get_value(1, 0)
    print(value)
    
    # Atualizando um valor
    test.update_value(1, 0, f"{contador+1}")
    
    # Obtendo um valor
    value = test.get_value(1, 0)
    print(int(value))
