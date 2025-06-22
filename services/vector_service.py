import logging
import numpy as np
import faiss
import requests
import json
import os
from typing import List, Dict, Any, Optional
import pickle

class VectorService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.environ.get('AITUNNEL_API_KEY', 'default-key')
        self.embeddings_url = "https://api.aitunnel.ai/v1/embeddings"
        
        # Initialize Faiss index
        self.dimension = 1536  # Common embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.materials_database = []
        
        # Load or create materials database
        self._initialize_materials_database()
    
    def _initialize_materials_database(self):
        """Initialize materials database with common engineering materials"""
        try:
            # Try to load existing database
            if os.path.exists('materials_db.pkl'):
                with open('materials_db.pkl', 'rb') as f:
                    data = pickle.load(f)
                    self.materials_database = data.get('materials', [])
                    if 'index' in data:
                        self.index = data['index']
                self.logger.info(f"Loaded materials database with {len(self.materials_database)} entries")
            else:
                # Create initial database with common materials
                self._create_initial_database()
        except Exception as e:
            self.logger.error(f"Error initializing materials database: {str(e)}")
            self._create_initial_database()
    
    def _create_initial_database(self):
        """Create initial materials database with common engineering materials"""
        initial_materials = [
            {
                "name": "Steel 45 (GOST 1050)",
                "description": "Carbon structural steel, widely used for shafts, gears, and machine parts",
                "properties": "Tensile strength: 600-700 MPa, Yield strength: 350-400 MPa",
                "applications": "Shafts, gears, bolts, machine parts under moderate loads",
                "gost_standards": ["GOST 1050-2013"]
            },
            {
                "name": "Steel 40X (GOST 4543)",
                "description": "Chromium alloy steel for improved hardenability",
                "properties": "High strength after heat treatment, good wear resistance",
                "applications": "Gears, shafts, crankshafts, high-strength bolts",
                "gost_standards": ["GOST 4543-2016"]
            },
            {
                "name": "Aluminum Alloy AMg6 (GOST 4784)",
                "description": "Magnesium-aluminum alloy with good corrosion resistance",
                "properties": "Light weight, corrosion resistant, good weldability",
                "applications": "Marine applications, chemical equipment, lightweight structures",
                "gost_standards": ["GOST 4784-2019"]
            },
            {
                "name": "Titanium VT1-0 (GOST 19807)",
                "description": "Pure titanium with excellent corrosion resistance",
                "properties": "High strength-to-weight ratio, corrosion resistant",
                "applications": "Chemical equipment, medical implants, aerospace",
                "gost_standards": ["GOST 19807-91"]
            },
            {
                "name": "Cast Iron SCh20 (GOST 1412)",
                "description": "Gray cast iron for general engineering applications",
                "properties": "Good machinability, vibration damping, low cost",
                "applications": "Machine bases, housings, brackets, covers",
                "gost_standards": ["GOST 1412-85"]
            }
        ]
        
        self.materials_database = initial_materials
        self.logger.info(f"Created initial materials database with {len(initial_materials)} entries")
    
    def get_embeddings(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        Get embeddings for texts using AiTunnel API
        
        Args:
            texts (List[str]): List of texts to embed
            
        Returns:
            np.ndarray: Array of embeddings or None if failed
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": texts,
                "model": "text-embedding-ada-002"
            }
            
            response = requests.post(self.embeddings_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                embeddings = [item['embedding'] for item in result['data']]
                return np.array(embeddings, dtype=np.float32)
            else:
                self.logger.error(f"Embeddings API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting embeddings: {str(e)}")
            return None
    
    def search_similar_materials(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar materials based on query
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to return
            
        Returns:
            List[Dict]: List of similar materials with scores
        """
        try:
            # Get query embedding
            query_embedding = self.get_embeddings([query])
            if query_embedding is None:
                return []
            
            # If index is empty, return all materials
            if self.index.ntotal == 0:
                return self.materials_database[:top_k]
            
            # Search in Faiss index
            distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.materials_database):
                    material = self.materials_database[idx].copy()
                    material['similarity_score'] = float(1.0 / (1.0 + distance))  # Convert distance to similarity
                    results.append(material)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching materials: {str(e)}")
            # Return fallback results
            return self.materials_database[:top_k]
    
    def add_material(self, material: Dict[str, Any]):
        """
        Add new material to the database
        
        Args:
            material (Dict): Material information
        """
        try:
            # Create text representation for embedding
            text = f"{material.get('name', '')} {material.get('description', '')} {material.get('properties', '')} {material.get('applications', '')}"
            
            # Get embedding
            embedding = self.get_embeddings([text])
            if embedding is not None:
                # Add to Faiss index
                self.index.add(embedding)
                
                # Add to materials database
                self.materials_database.append(material)
                
                # Save database
                self._save_database()
                
                self.logger.info(f"Added material: {material.get('name', 'Unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error adding material: {str(e)}")
    
    def _save_database(self):
        """Save materials database to file"""
        try:
            data = {
                'materials': self.materials_database,
                'index': self.index
            }
            with open('materials_db.pkl', 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error saving database: {str(e)}")
    
    def get_material_recommendations(self, requirements: str) -> List[Dict[str, Any]]:
        """
        Get material recommendations based on requirements
        
        Args:
            requirements (str): Material requirements description
            
        Returns:
            List[Dict]: Recommended materials
        """
        return self.search_similar_materials(requirements, top_k=3)
