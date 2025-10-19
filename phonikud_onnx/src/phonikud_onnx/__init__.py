from .model import OnnxModel
import re
import onnxruntime as ort


class Phonikud:
    def __init__(self, model_path: str):
        self.model = OnnxModel(model_path)

    @classmethod
    def from_session(cls, session: ort.InferenceSession):
        instance: "Phonikud" = cls.__new__(cls)
        instance.model = OnnxModel(model_path="", session=session)
        return instance

    def prepare_chunks(self, text: str) -> list[str]:
        """
        Split text into chunks no longer than 2046 characters.
        """
        if len(text) <= 2046:
            return [text]

        parts = re.split(r"(\.|\n)", text)
        chunks = []
        buf = ""

        for part in parts:
            if len(buf + part) <= 2046:
                buf += part
            else:
                if buf:
                    chunks.append(buf)
                buf = part
        if buf:
            chunks.append(buf)

        result = []
        for chunk in chunks:
            if len(chunk) <= 2046:
                result.append(chunk)
            else:
                result.extend([chunk[i : i + 2046] for i in range(0, len(chunk), 2046)])

        return result

    def add_diacritics(
        self, sentences: str | list[str], mark_matres_lectionis: str | None = None
    ) -> str | list[str]:
        """
        Adds nikud (Hebrew diacritics) to the given text.

        Parameters:
        - sentences (str | list[str]): A string or a list of strings to be processed. Each string should not exceed 2048 characters.
        - mark_matres_lectionis (str | None, optional): A string used to mark nikud male. For example, if set to '|',
            "לִימּוּדָיו" will be returned as "לִי|מּוּדָיו". Default is None (no marking).

        Returns:
        - str | list[str]: The text with added diacritics. Returns a string if input was a string, or a list if input was a list.
        """
        # Handle single string vs list
        is_single = isinstance(sentences, str)
        sentence_list = [sentences] if is_single else sentences
        
        # Prepare all chunks and track which sentence each chunk belongs to
        all_chunks = []
        chunk_to_sentence = []  # Maps chunk index to sentence index
        
        for sent_idx, sentence in enumerate(sentence_list):
            chunks = self.prepare_chunks(sentence)
            all_chunks.extend(chunks)
            chunk_to_sentence.extend([sent_idx] * len(chunks))
        
        # Batch process all chunks at once
        if all_chunks:
            batch_results = self.model.predict(all_chunks, mark_matres_lectionis=mark_matres_lectionis)
            
            # Reconstruct sentences from chunks
            all_results = [""] * len(sentence_list)
            for chunk_idx, result in enumerate(batch_results):
                sent_idx = chunk_to_sentence[chunk_idx]
                all_results[sent_idx] += result
        else:
            all_results = [""] * len(sentence_list)
        
        return all_results[0] if is_single else all_results

    def get_nikud_male(self, text: str, mark_matres_lectionis: str):
        """
        Based on given mark character remove the mark character to keep it as nikud male
        """
        return text.replace(mark_matres_lectionis, "")

    def get_nikud_haser(self, text: str):
        """
        Based on given mark_matres_lectionis remove the nikud nikud male character along with the mark character
        """
        return re.sub(r".\|", "", text)  # Remove {char}{matres_lectionis}

    def get_metadata(self):
        return self.model.get_metadata()
