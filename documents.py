from abc import ABC, abstractmethod
from typing import List, Union, Type, Dict, Callable
from pathlib import Path
import re
import docx2txt
import logging

log = logging.getLogger(__name__)

# Definir expresión regular para separadores de línea
PARAGRAPH_SEPARATOR_REGEX = re.compile(r"([^\n\r]*)[\n\r]+(.*)")
WORD_SEPARATOR_REGEX = re.compile(r"\s+")

def get_paragraphs(texto):
    # Patrón de división: un punto seguido de cualquier cantidad de espacios y tabulaciones, y un salto de línea
    patron_division = r'\.\s*\n'
    # Divide el texto según el patrón y también divide el texto al final
    partes = re.split(patron_division, texto.strip())

    # Filtra los elementos vacíos o llenos de espacios en blanco
    partes_filtradas = [parte.strip() for parte in partes if parte.strip()]
    
    return partes_filtradas
    
class Document(ABC):
    _file_type_registry: Dict[str, Type["Document"]] = {}

    def __init__(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as text_file:
            self.text = text_file.read()

    def __str__(self):
        return self.text
    
    def split_into_parts(self, max_words: int) -> List[str]:
        paragraphs = get_paragraphs(self.text)

        parts = []
        current_part = ""
        current_part_words_count = 0
        for paragraph in paragraphs: 

            paragraph_words = paragraph.split()
            paragraph_words_count = len(paragraph_words)

            if paragraph_words_count > max_words:
                raise ValueError("Párrafos más largos que el maximo permitido")

            if current_part_words_count + paragraph_words_count > max_words:
                parts.append(current_part)
            
            current_part += paragraph+"\n"
            current_part_words_count += paragraph_words_count
        
        return parts

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "Document":
        file_path = Path(file_path)
        file_suffix = file_path.suffix
        if file_suffix in cls._file_type_registry:
            return cls._file_type_registry[file_suffix](file_path)
        else:
            raise ValueError("El formato del archivo no es compatible.")

    @classmethod
    def register_file_type(cls, file_suffix: str) -> Callable[[Type["Document"]], Type["Document"]]:
        def decorator(document_type: Type["Document"]) -> Type["Document"]:
            cls._file_type_registry[file_suffix] = document_type
            return document_type
        return decorator

@Document.register_file_type(".txt")
class PlainTextDocument(Document):
    pass

@Document.register_file_type(".docx")
class WordDocument(Document):
    def __init__(self, file_path: str):
        with open(file_path, "rb") as doc_file:
            self.text = docx2txt.process(doc_file)
