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

import tiktoken

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


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

            paragraph_words_count = num_tokens_from_messages( [{"role": "system",
                                                               "content":paragraph}])

            if paragraph_words_count > max_words:
                raise ValueError("Párrafos más largos que el maximo permitido")

            if current_part_words_count + paragraph_words_count > max_words:
                parts.append(current_part)
                current_part = ""
                current_part_words_count = 0
                continue
            
            current_part += paragraph+"\n"
            current_part_words_count += paragraph_words_count
        
        if current_part:
            parts.append(current_part)

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
