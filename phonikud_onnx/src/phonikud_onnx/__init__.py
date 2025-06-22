from .model import OnnxModel
import re
import onnxruntime as ort


class Phonikud:
    def __init__(self, model_path: str):
        self.model = OnnxModel(model_path)

    @classmethod
    def from_session(cls, session: ort.InferenceSession):
        instance: 'Phonikud' = cls.__new__(cls)
        instance.model = OnnxModel(model_path='', session=session)
        return instance

    def add_diacritics(
        self, sentences: list | str, mark_matres_lectionis: str | None = None
    ) -> str:
        """
        Adds nikud (Hebrew diacritics) to the given text.

        Parameters:
        - sentences (list | str): A string or a list of strings to be processed. Each string should not exceed 2048 characters.
        - mark_matres_lectionis (str | None, optional): A string used to mark nikud male. For example, if set to '|',
            "לִימּוּדָיו" will be returned as "לִי|מּוּדָיו". Default is None (no marking).

        Returns:
        - str: The text with added diacritics.
        """

        if isinstance(sentences, str):
            sentences = [sentences]
        result = self.model.predict(
            sentences, mark_matres_lectionis=mark_matres_lectionis
        )
        return result[0]

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