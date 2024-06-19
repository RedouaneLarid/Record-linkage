import re
import jellyfish
import os

class Key :
    attribute_mapping = {'Name': 0, 'Surname': 1, 'Gender': 2, 'Age': 3, 'Region': 4, 'Job Classification': 5, 'Date Joined': 6, 'Balance': 7}  
    function_mapping = {jellyfish.soundex: 0, jellyfish.nysiis: 1, jellyfish.metaphone: 2, str: 3} 
    reverse_attribute_mapping = {v: k for k, v in attribute_mapping.items()}
    reverse_function_mapping = {v: k for k, v in function_mapping.items()}

    def __init__(self , block , attributes , functions , count):
        self.block = block

        self.attributes = attributes
        self.functions = functions 
        self.count = count 

        self.values = []
        self.score = None

    def __str__(self):
        return f"UUID: {self.block}\nAttributes: {self.attributes}\nFunctions: {self.functions}\nCount: {self.count}"
    
    def __eq__(self, other):
        if isinstance(other, Key):
            return self.attributes == other.attributes and self.functions == other.functions and self.count == other.count
        return False
    
    def __hash__(self):
        return hash(self.block)
    
    def to_position(self):
        # Encode attributes and functions as indices
        encoded_attributes = [self.attribute_mapping[attr] for attr in self.attributes]
        encoded_functions = [self.function_mapping[func] for func in self.functions]
        # Combine encoded attributes, functions, and counts into a single position vector
        position = [[encoded_attributes[i], encoded_functions[i], self.count[i]] for i in range(len(self.attributes))]
        return position
    
    @classmethod
    def from_position(cls , position , blk):
        # Decode the position back to attributes, functions, and counts
        decoded_attributes = [Key.reverse_attribute_mapping[pos[0]] for pos in position]
        decoded_functions = [Key.reverse_function_mapping[pos[1]] for pos in position]
        counts = [pos[2] for pos in position]
        return Key(blk, decoded_attributes, decoded_functions, counts)
    

    def Keyv(self , row):
        v = []
        for i, att in enumerate(self.attributes):
            value = str(row[att])[:self.count[i]]
            transformed_value = self.functions[i](value)
            v.append(transformed_value)
    
        result = Key.clean_string("".join(v))
        if result not in self.values:
            self.values.append(result)

        return result


    def clean_string(s):
        """Remove punctuation and spaces, and convert to lowercase."""
        s = re.sub(r'[^\w\s]', '', s)  # Remove punctuation
        return s.replace(" ", "").lower()
    


    def to_custom_format(self):
        lines = []
        for attr, func, cnt in zip(self.attributes, self.functions, self.count):
            lines.append(f"{attr}-{func}-{cnt}")
        return "\n".join(lines)

    def export_to_custom_format(self, folder_path, filename):
        # Ensure the directory exists
        os.makedirs(folder_path, exist_ok=True)
        
        # Construct the full file path
        file_path = os.path.join(folder_path, filename)
        
        # Write the formatted data to the file
        with open(file_path, mode='w') as file:
            file.write(self.to_custom_format())