import spacy
import re
import json
import logging
import argparse
import sys
from typing import Dict, List, Tuple, Any
from datetime import datetime
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification, 
    pipeline,
    AutoModelForSequenceClassification
)
import torch
from dataclasses import dataclass, asdict
import hashlib
import random
import string
from pathlib import Path
print("Script started")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RedactionResult:
    """Data class to store redaction results"""
    original_text: str
    redacted_text: str
    entities_found: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    redaction_summary: Dict[str, int]
    processing_time: float

class AdvancedRedactionModel:
    """
    Advanced AI-powered redaction tool using spaCy, regex, and transformers
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the redaction model with configuration"""
        self.config = config or self._get_default_config()
        self.spacy_model = None
        self.ner_pipeline = None
        self.classification_pipeline = None
        self.patterns = self._compile_regex_patterns()
        self.replacement_cache = {}
        
        # Load models
        self._load_models()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for the redaction model"""
        return {
            'spacy_model': 'en_core_web_sm',
            'huggingface_ner_model': 'dbmdz/bert-large-cased-finetuned-conll03-english',
            'huggingface_classification_model': 'microsoft/DialoGPT-medium',
            'confidence_threshold': 0.8,
            'redaction_char': '█',
            'preserve_format': True,
            'custom_entities': ['CREDIT_CARD', 'SSN', 'PHONE', 'EMAIL', 'IP_ADDRESS', 'API_KEY'],
            'replacement_strategy': 'consistent',  # 'consistent', 'random', 'hash'
            'use_transformers': True,
            'use_regex': True
        }
    
    def _load_models(self):
        """Load all required models"""
        try:
            # Load spaCy model
            logger.info(f"Loading spaCy model: {self.config['spacy_model']}")
            if Path(self.config['spacy_model']).exists():
                # Load custom trained model
                self.spacy_model = spacy.load(self.config['spacy_model'])
                logger.info("Custom trained model loaded")
            else:
                # Load standard model
                self.spacy_model = spacy.load(self.config['spacy_model'])
                logger.info("Standard spaCy model loaded")
            
            # Load Hugging Face NER pipeline (optional)
            if self.config.get('use_transformers', True):
                try:
                    logger.info(f"Loading HuggingFace NER model: {self.config['huggingface_ner_model']}")
                    self.ner_pipeline = pipeline(
                        "ner",
                        model=self.config['huggingface_ner_model'],
                        tokenizer=self.config['huggingface_ner_model'],
                        aggregation_strategy="simple",
                        device=0 if torch.cuda.is_available() else -1
                    )
                    logger.info("Transformer model loaded successfully")
                except Exception as e:
                    logger.warning(f"Could not load transformer model: {e}")
                    self.ner_pipeline = None
            
            logger.info("Models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def _compile_regex_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for various sensitive data types"""
        patterns = {
            'SSN': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            'CREDIT_CARD': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'PHONE': re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            'EMAIL': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'IP_ADDRESS': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'API_KEY': re.compile(r'\b[A-Za-z0-9]{32,}\b'),
            'URL': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'DATE': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'),
            'ZIP_CODE': re.compile(r'\b\d{5}(?:-\d{4})?\b'),
            'ACCOUNT_NUMBER': re.compile(r'\b\d{8,20}\b')
        }
        return patterns
    
    def _extract_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using spaCy"""
        doc = self.spacy_model(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': 0.9,  # spaCy doesn't provide confidence scores by default
                'source': 'spacy'
            })
        
        return entities
    
    def _extract_with_transformers(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using Hugging Face transformers"""
        if not self.ner_pipeline:
            return []
            
        try:
            results = self.ner_pipeline(text)
            entities = []
            
            for result in results:
                entities.append({
                    'text': result['word'],
                    'label': result['entity_group'],
                    'start': result['start'],
                    'end': result['end'],
                    'confidence': result['score'],
                    'source': 'transformers'
                })
            
            return entities
        
        except Exception as e:
            logger.warning(f"Error in transformer extraction: {str(e)}")
            return []
    
    def _extract_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using regex patterns"""
        if not self.config.get('use_regex', True):
            return []
            
        entities = []
        
        for pattern_name, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entities.append({
                    'text': match.group(),
                    'label': pattern_name,
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.95,  # High confidence for regex matches
                    'source': 'regex'
                })
        
        return entities
    
    def _merge_entities(self, entities_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Merge entities from different sources and remove duplicates"""
        all_entities = []
        for entities in entities_list:
            all_entities.extend(entities)
        
        # Sort by start position
        all_entities.sort(key=lambda x: x['start'])
        
        # Remove overlapping entities (keep highest confidence)
        merged = []
        for entity in all_entities:
            # Check for overlap with existing entities
            overlap = False
            for existing in merged:
                if (entity['start'] < existing['end'] and 
                    entity['end'] > existing['start']):
                    # There's an overlap
                    if entity['confidence'] > existing['confidence']:
                        # Replace existing with current
                        merged.remove(existing)
                        merged.append(entity)
                    overlap = True
                    break
            
            if not overlap:
                merged.append(entity)
        
        return sorted(merged, key=lambda x: x['start'])
    
    def _generate_replacement(self, entity: Dict[str, Any]) -> str:
        """Generate replacement text for an entity"""
        text = entity['text']
        label = entity['label']
        
        if self.config['replacement_strategy'] == 'consistent':
            # Use cache for consistent replacements
            cache_key = f"{label}_{text.lower()}"
            if cache_key in self.replacement_cache:
                return self.replacement_cache[cache_key]
        
        # Generate replacement based on entity type
        if label in ['PERSON', 'PER']:
            replacement = f"[PERSON_{len(self.replacement_cache) + 1}]"
        elif label in ['ORG', 'ORGANIZATION']:
            replacement = f"[ORGANIZATION_{len(self.replacement_cache) + 1}]"
        elif label in ['SSN']:
            replacement = "XXX-XX-XXXX"
        elif label in ['CREDIT_CARD']:
            replacement = "XXXX-XXXX-XXXX-XXXX"
        elif label in ['PHONE']:
            replacement = "(XXX) XXX-XXXX"
        elif label in ['EMAIL']:
            replacement = "[EMAIL_REDACTED]"
        elif label in ['IP_ADDRESS']:
            replacement = "XXX.XXX.XXX.XXX"
        else:
            # Generic redaction
            if self.config['preserve_format']:
                replacement = self.config['redaction_char'] * len(text)
            else:
                replacement = f"[{label}_REDACTED]"
        
        # Cache the replacement
        if self.config['replacement_strategy'] == 'consistent':
            cache_key = f"{label}_{text.lower()}"
            self.replacement_cache[cache_key] = replacement
        
        return replacement
    
    def redact_text(self, text: str) -> RedactionResult:
        """Main method to redact sensitive information from text"""
        start_time = datetime.now()
        
        logger.info("Starting redaction process...")
        
        # Extract entities using all methods
        spacy_entities = self._extract_with_spacy(text)
        transformer_entities = self._extract_with_transformers(text)
        regex_entities = self._extract_with_regex(text)
        
        logger.info(f"Found {len(spacy_entities)} spaCy entities")
        logger.info(f"Found {len(transformer_entities)} transformer entities")
        logger.info(f"Found {len(regex_entities)} regex entities")
        
        # Merge all entities
        all_entities = self._merge_entities([spacy_entities, transformer_entities, regex_entities])
        
        # Filter by confidence threshold
        filtered_entities = [
            entity for entity in all_entities 
            if entity['confidence'] >= self.config['confidence_threshold']
        ]
        
        logger.info(f"After filtering: {len(filtered_entities)} entities")
        
        # Perform redaction
        redacted_text = text
        offset = 0
        
        for entity in filtered_entities:
            start = entity['start'] + offset
            end = entity['end'] + offset
            
            replacement = self._generate_replacement(entity)
            
            redacted_text = (
                redacted_text[:start] + 
                replacement + 
                redacted_text[end:]
            )
            
            # Update offset for next replacement
            offset += len(replacement) - (entity['end'] - entity['start'])
        
        # Calculate summary statistics
        entity_counts = {}
        confidence_scores = {}
        
        for entity in filtered_entities:
            label = entity['label']
            entity_counts[label] = entity_counts.get(label, 0) + 1
            
            if label not in confidence_scores:
                confidence_scores[label] = []
            confidence_scores[label].append(entity['confidence'])
        
        # Average confidence scores
        avg_confidence_scores = {
            label: sum(scores) / len(scores) 
            for label, scores in confidence_scores.items()
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Redaction completed in {processing_time:.2f} seconds")
        
        return RedactionResult(
            original_text=text,
            redacted_text=redacted_text,
            entities_found=filtered_entities,
            confidence_scores=avg_confidence_scores,
            redaction_summary=entity_counts,
            processing_time=processing_time
        )
def main():
    # Initialize the model with defaults or customize as needed
    redactor = AdvancedRedactionModel()

    print("Redaction model loaded.")
    print("Enter text to redact (type 'exit' to quit):")

    while True:
        try:
            text = input(">> ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if text.strip().lower() == 'exit':
            print("Exiting...")
            break

        if not text.strip():
            print("Please enter some text.")
            continue

        result = redactor.redact_text(text)
        print("\nOriginal Text:")
        print(result.original_text)
        print("\nRedacted Text:")
        print(result.redacted_text)
        print("\nEntities Found:")
        for entity in result.entities_found:
            print(f"  - {entity['text']} ({entity['label']})")
        print()

if __name__ == "__main__":
    main()
