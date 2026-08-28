
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Path to the trained model
MODEL_PATH = "/content/drive/MyDrive/ScienceQA_Project/Member1_Domain_Classifier/science_domain_model"

# Label mapping used by the trained model
ID2LABEL = {
    0: "Biology",
    1: "Chemistry",
    2: "Earth Science",
    3: "Physics"
}

# Load tokenizer and trained model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()


def classify_topic(topic):
    """
    Classify a science topic into:
    Biology, Chemistry, Earth Science, or Physics.

    Returns:
        domain, confidence
    """

    inputs = tokenizer(
        topic,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=-1)
    predicted_id = torch.argmax(probabilities, dim=-1).item()
    confidence = probabilities[0][predicted_id].item()

    domain = ID2LABEL[predicted_id]

    return domain, confidence


if __name__ == "__main__":
    domain, confidence = classify_topic("Chemical Bonding")

    print("Topic: Chemical Bonding")
    print("Domain:", domain)
    print("Confidence:", round(confidence, 4))
