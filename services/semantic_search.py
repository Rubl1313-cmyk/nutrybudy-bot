"""
🔍 Семантический поиск по базе продуктов
Использует эмбеддинги для поиска похожих продуктов
"""
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
import os
import pickle

logger = logging.getLogger(__name__)

class SemanticSearchEngine:
    """Семантический поиск по базе продуктов"""
    
    def __init__(self):
        self.model = None
        self.embeddings = None
        self.product_names = []
        self.model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        self.cache_file = "data/semantic_cache.pkl"
        
    def _load_model(self):
        """Загружает модель эмбеддингов"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"🔍 Загружена модель: {self.model_name}")
            return True
        except ImportError:
            logger.warning("🔍 sentence-transformers не установлен, семантический поиск недоступен")
            return False
        except Exception as e:
            logger.error(f"🔍 Ошибка загрузки модели: {e}")
            return False
    
    def _load_embeddings(self):
        """Загружает предвычисленные эмбеддинги"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.embeddings = data['embeddings']
                    self.product_names = data['product_names']
                logger.info(f"🔍 Загружены эмбеддинги для {len(self.product_names)} продуктов")
                return True
        except Exception as e:
            logger.warning(f"🔍 Не удалось загрузить эмбеддинги: {e}")
        return False
    
    def _save_embeddings(self):
        """Сохраняет эмбеддинги в кэш"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                pickle.dump({
                    'embeddings': self.embeddings,
                    'product_names': self.product_names
                }, f)
            logger.info(f"🔍 Сохранены эмбеддинги для {len(self.product_names)} продуктов")
        except Exception as e:
            logger.error(f"🔍 Ошибка сохранения эмбеддингов: {e}")
    
    def _build_embeddings(self, food_db: Dict):
        """Строит эмбеддинги для базы продуктов"""
        if not self._load_model():
            return False
        
        logger.info("🔍 Построение эмбеддингов для базы продуктов...")
        
        # Собираем все названия продуктов
        self.product_names = []
        for product_key, product_data in food_db.items():
            if isinstance(product_data, dict):
                # Добавляем основное название
                self.product_names.append(product_data.get('name', product_key))
                
                # Добавляем синонимы если есть
                aliases = product_data.get('aliases', [])
                if isinstance(aliases, list):
                    self.product_names.extend(aliases)
                elif isinstance(aliases, str):
                    self.product_names.append(aliases)
            else:
                self.product_names.append(product_key)
        
        # Удаляем дубликаты и пустые значения
        self.product_names = list(set([name for name in self.product_names if name and name.strip()]))
        
        if not self.product_names:
            logger.warning("🔍 Не найдено названий продуктов для эмбеддингов")
            return False
        
        # Вычисляем эмбеддинги
        try:
            self.embeddings = self.model.encode(
                self.product_names,
                normalize_embeddings=True,
                show_progress_bar=True
            )
            logger.info(f"🔍 Вычислены эмбеддинги для {len(self.product_names)} продуктов")
            
            # Сохраняем в кэш
            self._save_embeddings()
            return True
            
        except Exception as e:
            logger.error(f"🔍 Ошибка вычисления эмбеддингов: {e}")
            return False
    
    def initialize(self, food_db: Dict):
        """Инициализирует семантический поиск"""
        logger.info("🔍 Инициализация семантического поиска...")
        
        # Пробуем загрузить из кэша
        if not self._load_embeddings():
            # Если кэша нет, строим эмбеддинги
            if not self._build_embeddings(food_db):
                logger.warning("🔍 Семантический поиск недоступен")
                return False
        
        return True
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.5) -> List[Tuple[str, float]]:
        """
        Ищет похожие продукты
        
        Args:
            query: Запрос пользователя
            top_k: Количество результатов
            threshold: Порог сходства
            
        Returns:
            Список кортежей (название_продукта, сходство)
        """
        if not self.model or self.embeddings is None:
            logger.warning("🔍 Семантический поиск не инициализирован")
            return []
        
        try:
            # Вычисляем эмбеддинг запроса
            query_embedding = self.model.encode([query], normalize_embeddings=True)
            
            # Вычисляем косинусное сходство
            similarities = np.dot(self.embeddings, query_embedding.T).flatten()
            
            # Получаем топ-k результатов
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                similarity = float(similarities[idx])
                if similarity >= threshold:
                    product_name = self.product_names[idx]
                    results.append((product_name, similarity))
            
            logger.info(f"🔍 Найдено {len(results)} похожих продуктов для '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"🔍 Ошибка семантического поиска: {e}")
            return []

# Глобальный экземпляр
semantic_search = SemanticSearchEngine()

def initialize_semantic_search(food_db: Dict) -> bool:
    """Инициализирует семантический поиск"""
    return semantic_search.initialize(food_db)

def semantic_search_products(query: str, top_k: int = 5, threshold: float = 0.5) -> List[Tuple[str, float]]:
    """Выполняет семантический поиск продуктов"""
    return semantic_search.search(query, top_k, threshold)
