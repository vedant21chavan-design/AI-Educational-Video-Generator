# Member 1 - Science Domain Classification

## Objective

Member 1 is responsible for classifying a science question into one of four science domains before it is passed to the next stage of the text-to-video pipeline.

## Science Domains

The model classifies questions into:

1. Biology
2. Chemistry
3. Earth Science
4. Physics

Astronomy was excluded from the project scope.

## Dataset

The project uses the ScienceQA dataset.

After filtering and preprocessing, the final dataset contains:

- Training: 2,519 questions
- Validation: 723 questions
- Test: 609 questions
- Total: 3,851 questions

## Data Preprocessing

The following preprocessing steps were performed:

- Selected science-related questions
- Selected the four required domains
- Removed unwanted categories
- Removed duplicate/conflicting examples
- Checked for overlap between train, validation and test sets
- Converted domain names into numerical labels
- Tokenized questions using the DistilBERT tokenizer

## Model

The classification model used is:

`distilbert-base-uncased`

The pretrained DistilBERT model was fine-tuned for four-class science domain classification.

## Label Mapping

| Label | Domain |
|------:|--------|
| 0 | Biology |
| 1 | Chemistry |
| 2 | Earth Science |
| 3 | Physics |

## Training

Training was performed using a Tesla T4 GPU.

The model was trained for 4 epochs with:

- Batch size: 16
- Learning rate: 2e-5
- Weight decay: 0.01
- FP16 enabled

## Evaluation

On the prepared test set of 609 questions, the model achieved:

- Accuracy: 100%
- Precision: 100%
- Recall: 100%
- F1-score: 100%

## Output

The Member 1 module accepts a science question and returns:

- Original question
- Predicted science domain
- Prediction confidence

Example:

Input:

"What causes an object to accelerate?"

Output:

"Physics"

## Role in the Text-to-Video Pipeline

User Question
       ↓
Member 1: Science Domain Classification
       ↓
Biology / Chemistry / Earth Science / Physics
       ↓
Next Module
       ↓
Text-to-Video Generation
