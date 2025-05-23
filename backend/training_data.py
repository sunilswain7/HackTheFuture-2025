import json
import random
import string
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TrainingExample:
    """Data class for training examples"""
    text: str
    entities: List[Dict[str, Any]]
    labels: List[str]

class TrainingDataGenerator:
    """Generate synthetic training data for redaction model"""
    
    def __init__(self):
        self.person_names = [
            "John Smith", "Jane Doe", "Michael Johnson", "Sarah Wilson",
            "David Brown", "Emily Davis", "Robert Miller", "Lisa Anderson",
            "Christopher Taylor", "Jennifer Thomas", "Matthew Jackson",
            "Ashley White", "Daniel Harris", "Jessica Martin", "James Thompson"
        ]
        
        self.organizations = [
            "Acme Corporation", "TechCorp Inc", "Global Industries",
            "Innovation LLC", "DataSoft Solutions", "SecureBank",
            "HealthCare Systems", "EduTech Institute", "RetailMax",
            "ServiceFirst Company", "Manufacturing Co", "Consulting Group"
        ]
        
        # More diverse domain list
        self.domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "company.com", "startup.tech", "research.org", "school.edu",
            "internal.corp", "gov.agency", "freemail.xyz", "bizmail.co.uk",
            "custom.io", "service.in", "email.de"
        ]
    
    def generate_ssn(self) -> str:
        """Generate a fake SSN"""
        return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    
    def generate_phone(self) -> str:
        """Generate a fake phone number"""
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        
        formats = [
            f"({area_code}) {exchange}-{number}",
            f"{area_code}-{exchange}-{number}",
            f"{area_code}.{exchange}.{number}",
            f"{area_code} {exchange} {number}"
        ]
        return random.choice(formats)
    
    def generate_email(self, name: str = None) -> str:
        """Generate a fake email address with random and known domains"""
        if name:
            username = name.lower().replace(" ", ".")
        else:
            username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
        
        # 50% chance known domain, 50% chance random domain
        if random.random() < 0.5:
            domain = random.choice(self.domains)
        else:
            domain_prefix = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
            tld = random.choice(['com', 'net', 'org', 'io', 'co', 'ai', 'de', 'uk', 'in', 'edu'])
            domain = f"{domain_prefix}.{tld}"
        
        return f"{username}@{domain}"
    
    def generate_credit_card(self) -> str:
        """Generate a fake credit card number"""
        number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        
        formats = [
            f"{number[:4]}-{number[4:8]}-{number[8:12]}-{number[12:]}",
            f"{number[:4]} {number[4:8]} {number[8:12]} {number[12:]}",
            number
        ]
        return random.choice(formats)
    
    def generate_api_key(self) -> str:
        """Generate a fake API key"""
        length = random.randint(32, 64)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def generate_ip_address(self) -> str:
        """Generate a fake IP address"""
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
    
    def generate_training_example(self) -> TrainingExample:
        person = random.choice(self.person_names)
        organization = random.choice(self.organizations)
        phone = self.generate_phone()
        email = self.generate_email(person)
        ssn = self.generate_ssn()
        credit_card = self.generate_credit_card()
        api_key = self.generate_api_key()
        ip_address = self.generate_ip_address()
        
        templates = [
            f"{person} works at {organization}. Contact: {phone}, {email}. SSN: {ssn}",
            f"Employee {person} from {organization} has credit card {credit_card} and phone {phone}",
            f"User {person} ({email}) at {organization} uses API key {api_key}",
            f"{person}'s details: Phone {phone}, Email {email}, SSN {ssn}, Company {organization}",
            f"API access for {person} at {organization}: Key {api_key}, IP {ip_address}"
        ]
        
        text = random.choice(templates)
        
        entities = []
        labels = []
        
        def add_entity(entity_text: str, entity_type: str):
            start = text.find(entity_text)
            if start != -1:
                entities.append({
                    'start': start,
                    'end': start + len(entity_text),
                    'text': entity_text,
                    'label': entity_type
                })
                labels.append(entity_type)
        
        add_entity(person, 'PERSON')
        add_entity(organization, 'ORG')
        add_entity(phone, 'PHONE')
        add_entity(email, 'EMAIL')
        add_entity(ssn, 'SSN')
        add_entity(credit_card, 'CREDIT_CARD')
        add_entity(api_key, 'API_KEY')
        add_entity(ip_address, 'IP_ADDRESS')
        
        return TrainingExample(
            text=text,
            entities=entities,
            labels=list(set(labels))
        )
    
    def generate_batch(self, num_examples: int) -> List[TrainingExample]:
        return [self.generate_training_example() for _ in range(num_examples)]
    
    def save_training_data(self, examples: List[TrainingExample], filename: str):
        data = []
        for example in examples:
            data.append({
                'text': example.text,
                'entities': example.entities,
                'labels': example.labels
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(examples)} training examples to {filename}")
    
    def load_training_data(self, filename: str) -> List[TrainingExample]:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        examples = []
        for item in data:
            examples.append(TrainingExample(
                text=item['text'],
                entities=item['entities'],
                labels=item['labels']
            ))
        
        logger.info(f"Loaded {len(examples)} training examples from {filename}")
        return examples

def main():
    generator = TrainingDataGenerator()
    
    print("Generating training data...")
    examples = generator.generate_batch(100)
    
    generator.save_training_data(examples, 'training_data.json')
    
    print("\nSample training examples:")
    for i, example in enumerate(examples[:3], 1):
        print(f"\nExample {i}:")
        print(f"Text: {example.text}")
        print(f"Entities: {len(example.entities)}")
        print(f"Labels: {example.labels}")

if __name__ == "__main__":
    main()
