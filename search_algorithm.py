# search_algorithm.py
from collections import defaultdict
from typing import List, Dict, Tuple
import heapq
from rapidfuzz import fuzz, process
from spellchecker import SpellChecker
import random
import numpy as np

class MicroLanguageModel:
    """Tiny neural language model for command decision making"""
    def __init__(self, vocab_size=1000, embed_size=16):
        # Tiny embedding layer
        self.embeddings = np.random.randn(vocab_size, embed_size) * 0.01
        # Tiny attention weights
        self.attention_weights = np.random.randn(embed_size) * 0.01
        # Tiny classifier
        self.classifier = np.random.randn(embed_size, 3) * 0.01  # 3 features
    
    def forward(self, word_indices):
        """Simple forward pass with attention"""
        if not word_indices:
            return [0.33, 0.33, 0.33]  # Neutral probabilities
        
        # Get embeddings
        embedded = np.mean([self.embeddings[idx % len(self.embeddings)] for idx in word_indices], axis=0)
        
        # Tiny attention
        attention_scores = np.dot(embedded, self.attention_weights)
        attention_weights = np.exp(attention_scores) / np.sum(np.exp(attention_scores))
        
        # Weighted features
        features = np.dot(embedded * attention_weights, self.classifier)
        return 1 / (1 + np.exp(-features))  # Sigmoid

class CommandSearcher:
    def __init__(self):
        self.word_index = defaultdict(set)
        self.command_keywords = []
        self.spell_checker = SpellChecker()
        self.all_words = []
        self.word_to_idx = {}
        self.lm = None
        
    def build_index(self, commands: List[Dict]) -> None:
        self.word_index = defaultdict(set)
        self.command_keywords = []
        self.all_words = []
        self.word_to_idx = {}
        
        # Build vocabulary
        vocab = set()
        for cmd in commands:
            search_text = f"{cmd.get('intent','')} {cmd.get('command','')} {cmd.get('description','')}"
            vocab.update(self._tokenize(search_text))
        
        self.all_words = list(vocab)
        self.word_to_idx = {word: idx for idx, word in enumerate(self.all_words)}
        self.spell_checker.word_frequency.load_words(self.all_words)
        
        # Initialize tiny language model
        self.lm = MicroLanguageModel(vocab_size=len(self.all_words))
        
        # Build command index
        for idx, cmd in enumerate(commands):
            search_text = f"{cmd.get('intent','')} {cmd.get('command','')} {cmd.get('description','')}"
            words = self._tokenize(search_text)
            
            for word in words:
                self.word_index[word].add(idx)
            
            self.command_keywords.append(set(words))
    
    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        return list(set(word.strip('.,!?()[]{}').lower() 
                     for word in text.split() 
                     if len(word.strip('.,!?()[]{}')) > 2))
    
    def _correct_spelling(self, word: str) -> str:
        if word in self.word_to_idx:
            return word
        
        correction = self.spell_checker.correction(word)
        if correction and correction in self.word_to_idx:
            return correction
        
        best_match, score, _ = process.extractOne(word, self.all_words, scorer=fuzz.WRatio)
        return best_match if score > 80 else word
    
    def _get_word_indices(self, words: List[str]) -> List[int]:
        """Convert words to indices for language model"""
        return [self.word_to_idx[word] for word in words if word in self.word_to_idx]
    
    def _analyze_with_lm(self, query_words: List[str], cmd_words: set) -> float:
        """Use language model to analyze relevance"""
        # Get word indices for language model
        query_indices = self._get_word_indices(query_words)
        cmd_indices = self._get_word_indices(list(cmd_words))
        
        # Get features from language model
        query_features = self.lm.forward(query_indices)
        cmd_features = self.lm.forward(cmd_indices)
        
        # Simple cosine similarity
        similarity = np.dot(query_features, cmd_features) / (
            np.linalg.norm(query_features) * np.linalg.norm(cmd_features) + 1e-6)
        
        return (similarity + 1) / 2  # Normalize to 0-1 range
    
    def search(self, query: str, commands: List[Dict]) -> List[Tuple[Dict, float]]:
        if not query.strip():
            return []
        
        # Process query
        query_words = []
        for word in self._tokenize(query):
            corrected = self._correct_spelling(word)
            if corrected:
                query_words.append(corrected)
        
        if not query_words:
            return []
        
        # Find candidates
        candidate_indices = set()
        for word in query_words:
            candidate_indices.update(self.word_index.get(word, set()))
        
        # Score candidates
        scored_results = []
        for idx in candidate_indices:
            cmd_words = self.command_keywords[idx]
            matched_words = set(query_words) & cmd_words
            
            # Language model analysis
            lm_score = self._analyze_with_lm(query_words, cmd_words)
            
            # Traditional features
            coverage = len(matched_words) / len(query_words)
            density = len(matched_words) / len(cmd_words) if cmd_words else 0
            
            # Combined score (weighted average)
            score = (lm_score * 0.6) + (coverage * 0.3) + (density * 0.1)
            
            if score > 0.3:  # Higher threshold for precision
                heapq.heappush(scored_results, (-score, idx))
        
        # Return top results
        return [
            (commands[idx], -score)
            for score, idx in sorted(scored_results, key=lambda x: x[0])[:3]
        ]
