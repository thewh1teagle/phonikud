# PhoNikud

Train model: `python src/train.py`

Test model: `python src/test.py`

TODO:
* Add documentation
* Refactoring:
  * Make PhonikudModel class extending BertForDiacritization
  * Organize train/val/test splits -- track val performance over time, log to tensorboard/wandb, ...
* Clean up flags in scripts