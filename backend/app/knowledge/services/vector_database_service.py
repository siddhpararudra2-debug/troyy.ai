"""
Vector Database Service
"""
import json


class VectorDatabaseService:
    @staticmethod
    def add_embedding(id: str, content: str, vector: list):
        return True

    @staticmethod
    def search_similar(query_embedding: list, top_k: int = 10):
        return []
