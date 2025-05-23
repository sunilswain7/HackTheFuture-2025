import spacy
import json
import logging
import argparse
import sys
from typing import Dict, List, Any, Tuple
from pathlib import Path
from spacy.training import Example
from spacy.util import minibatch, compounding
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedactionModelTrainer:
    """Train custom redaction models"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize trainer with base model"""
        self.model_name = model_name
        self.nlp = None
        self.training_data = []
        
    def load_base_model(self):
        """Load the base spaCy model"""
        try:
            logger.info(f"Loading base model: {self.model_name}")
            self.nlp = spacy.load(self.model_name)
            logger.info("Base model loaded successfully")
        except OSError:
            logger.error(f"Model {self.model_name} not found. Please install it first.")
            logger.info("Run: python -m spacy download en_core_web_sm")
            sys.exit(1)
    
    def load_training_data(self, data_file: str):
        """Load training data from JSON file"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to spaCy format
            self.training_data = []
            for item in data:
                text = item['text']
                entities = item['entities']
                
                # Convert entities to spaCy format
                spacy_entities = []
                for ent in entities:
                    spacy_entities.append((ent['start'], ent['end'], ent['label']))
                
                self.training_data.append((text, {'entities': spacy_entities}))
            
            logger.info(f"Loaded {len(self.training_data)} training examples")
            
        except FileNotFoundError:
            logger.error(f"Training data file {data_file} not found")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in {data_file}")
            sys.exit(1)
    
    def prepare_training_data(self) -> List[Example]:
        """Prepare training data for spaCy"""
        examples = []
        
        for text, annotations in self.training_data:
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        return examples
    
    def train_ner_model(self, 
                       output_dir: str, 
                       n_iter: int = 100,
                       dropout: float = 0.5,
                       batch_size: int = 4):
        """Train the NER model"""
        
        if not self.nlp:
            self.load_base_model()
        
        # Get the NER component
        if 'ner' not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe('ner', last=True)
        else:
            ner = self.nlp.get_pipe('ner')
        
        # Add labels to NER
        labels = set()
        for _, annotations in self.training_data:
            for ent in annotations.get('entities', []):
                labels.add(ent[2])
        
        for label in labels:
            ner.add_label(label)
        
        logger.info(f"Training with labels: {labels}")
        
        # Prepare training data
        examples = self.prepare_training_data()
        
        # Get other pipes to disable during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != 'ner']
        
        # Training loop
        logger.info(f"Starting training for {n_iter} iterations...")
        
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.resume_training()
            
            for iteration in range(n_iter):
                logger.info(f"Iteration {iteration + 1}/{n_iter}")
                
                # Shuffle training data
                random.shuffle(examples)
                
                losses = {}
                batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    self.nlp.update(batch, drop=dropout, losses=losses, sgd=optimizer)
                
                if (iteration + 1) % 10 == 0:
                    logger.info(f"Losses at iteration {iteration + 1}: {losses}")
        
        # Save the trained model
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.nlp.to_disk(output_path)
        logger.info(f"Model saved to {output_path}")
        
        return output_path
    
    def evaluate_model(self, test_data_file: str = None) -> Dict[str, float]:
        """Evaluate the trained model"""
        if test_data_file:
            # Load test data
            with open(test_data_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        else:
            # Use a portion of training data for evaluation
            test_data = self.training_data[:len(self.training_data) // 5]
        
        # Evaluate
        examples = []
        for item in test_data:
            if isinstance(item, dict):
                text = item['text']
                entities = [(ent['start'], ent['end'], ent['label']) for ent in item['entities']]
                annotations = {'entities': entities}
            else:
                text, annotations = item
            
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        # Get scores
        scores = self.nlp.evaluate(examples)
        
        logger.info("Evaluation Results:")
        logger.info(f"Precision: {scores['ents_p']:.3f}")
        logger.info(f"Recall: {scores['ents_r']:.3f}")
        logger.info(f"F1-Score: {scores['ents_f']:.3f}")
        
        return {
            'precision': scores['ents_p'],
            'recall': scores['ents_r'],
            'f1_score': scores['ents_f']
        }
    
    def test_model(self, test_text: str):
        """Test the model on sample text"""
        doc = self.nlp(test_text)
        
        print(f"\nTest Text: {test_text}")
        print("Entities found:")
        for ent in doc.ents:
            print(f"  {ent.text} -> {ent.label_} (confidence: {ent._.confidence if hasattr(ent._, 'confidence') else 'N/A'})")

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train redaction model')
    parser.add_argument('--data', required=True, help='Training data JSON file')
    parser.add_argument('--output', required=True, help='Output directory for trained model')
    parser.add_argument('--base-model', default='en_core_web_sm', help='Base spaCy model')
    parser.add_argument('--iterations', type=int, default=100, help='Number of training iterations')
    parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate')
    parser.add_argument('--batch-size', type=int, default=4, help='Batch size')
    parser.add_argument('--test-data', help='Test data file for evaluation')
    parser.add_argument('--test-text', help='Sample text to test the model')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = RedactionModelTrainer(args.base_model)
    
    # Load training data
    trainer.load_training_data(args.data)
    
    # Train model
    model_path = trainer.train_ner_model(
        output_dir=args.output,
        n_iter=args.iterations,
        dropout=args.dropout,
        batch_size=args.batch_size
    )
    
    # Evaluate model
    if args.test_data:
        scores = trainer.evaluate_model(args.test_data)
        print(f"\nEvaluation Results: {scores}")
    
    # Test model
    if args.test_text:
        trainer.test_model(args.test_text)
    
    print(f"\nTraining completed! Model saved to: {model_path}")
    print("To use the model:")
    print(f"  python redact.py --model {model_path} --text 'Your text here'")

if __name__ == "__main__":
    main()