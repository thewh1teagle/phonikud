# PhoNikud

Train model: `python src/train.py`

Test model: `python src/test.py`

TODO:
* Add documentation
* Implement:
  * save trained model checkpoint (extend BertForDiacritization, use transformers save_model())
  * test.py
* Refactoring:
  * Make PhonikudModel class extending BertForDiacritization, override predict method to include new outputs rather than current monkey-patch, extend MenakedLogitsOutput -- based on [this code](https://huggingface.co/dicta-il/dictabert-large-char-menaked/blob/main/BertForDiacritization.py)
  * Organize train/val/test splits -- track val performance over time, log to tensorboard/wandb, ...
  * Move utils like `is_hebrew_letter`, stress character value etc. into a separate script (`hebrew_utils.py`?)
* Clean up flags in scripts
* Check that stress/shva targets are guaranteed to be aligned with tokenized characters (use `return_offsets_mapping=True`? cf. dictabert code)