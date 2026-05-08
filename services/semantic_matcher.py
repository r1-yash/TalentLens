import numpy as np
from typing import Dict, List, Union
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from core.logger import get_logger
from core.config import settings

logger = get_logger(__name__)

class SemanticMatcher:
    """
    A lightweight semantic matching engine using SentenceTransformers and Scikit-Learn.
    Computes cosine similarity between Job Descriptions and Candidate Resumes.
    """
    def __init__(self, model_name: str = None):
        target_model = model_name or settings.embedding_model_name
        logger.info(f"Initializing SemanticMatcher with model: {target_model}")
        try:
            # Downloads/loads the model. Native Python 3.13 compatibility via PyTorch.
            self.model = SentenceTransformer(target_model)
        except Exception as e:
            logger.error(f"Failed to load embedding model {target_model}: {e}")
            raise

    def get_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generates embeddings for a given string or list of strings.
        Returns a 2D numpy array [1, dimension].
        """
        if not text:
            logger.warning("Empty text provided for embedding.")
            # Return a zero vector to gracefully prevent math errors
            return np.zeros((1, self.model.get_sentence_embedding_dimension()))
            
        if isinstance(text, list):
            # Combine lists into a single semantic block
            text = " ".join([str(t) for t in text if t])
            
        try:
            # .encode returns a 1D array. Wrap in list to get 2D array [1, dimension]
            embedding = self.model.encode([text])
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return np.zeros((1, self.model.get_sentence_embedding_dimension()))

    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Computes cosine similarity between two 2D numpy arrays.
        Returns a float between -1.0 and 1.0.
        """
        try:
            # sklearn expects 2D arrays: shape (n_samples_X, n_features)
            similarity = cosine_similarity(vec1, vec2)
            # We are comparing a single pair, so extract the [0][0] value
            return float(similarity[0][0])
        except Exception as e:
            logger.error(f"Error computing cosine similarity: {e}")
            return 0.0

    def match_candidate(self, 
                        jd_full_text: str, 
                        jd_skills: List[str], 
                        jd_experience: str,
                        resume_full_text: str, 
                        resume_skills: str, 
                        resume_experience: str) -> Dict[str, float]:
        """
        Calculates similarity across three distinct dimensions.
        """
        logger.debug("Generating embeddings for JD and Resume sections...")
        
        # 1. Overall Match
        jd_full_emb = self.get_embedding(jd_full_text)
        res_full_emb = self.get_embedding(resume_full_text)
        overall_sim = self.compute_similarity(jd_full_emb, res_full_emb)
        
        # 2. Skills Match
        jd_skills_emb = self.get_embedding(jd_skills)
        res_skills_emb = self.get_embedding(resume_skills)
        skills_sim = self.compute_similarity(jd_skills_emb, res_skills_emb)
        
        # 3. Experience Match
        jd_exp_emb = self.get_embedding(jd_experience)
        res_exp_emb = self.get_embedding(resume_experience)
        exp_sim = self.compute_similarity(jd_exp_emb, res_exp_emb)
        
        result = {
            "overall_similarity": round(overall_sim, 4),
            "skills_similarity": round(skills_sim, 4),
            "experience_similarity": round(exp_sim, 4)
        }
        
        logger.info(f"Candidate match scores computed: {result}")
        return result
