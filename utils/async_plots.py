"""
Асинхронная генерация графиков с matplotlib
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import asyncio
import io
import base64
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Настройка стилей
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AsyncPlotGenerator:
    """Асинхронный генератор графиков"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)  # 2 потока для графиков
    
    async def generate_progress_plot(self, data: Dict[str, List], period: str = "week") -> str:
        """Генерация графика прогресса в base64"""
        loop = asyncio.get_event_loop()
        
        try:
            # Выполняем в отдельном потоке
            plot_data = await loop.run_in_executor(
                self.executor, 
                self._create_progress_plot_sync, 
                data, 
                period
            )
            return plot_data
        except Exception as e:
            logger.error(f"Error generating progress plot: {e}")
            return self._create_error_plot()
    
    def _create_progress_plot_sync(self, data: Dict[str, List], period: str) -> str:
        """Синхронное создание графика прогресса"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'Прогресс за {period}', fontsize=16, fontweight='bold')
            
            # График калорий
            if 'calories' in data:
                dates = data['calories']['dates']
                calories = data['calories']['values']
                goal = data['calories'].get('goal', 2000)
                
                ax1.plot(dates, calories, marker='o', linewidth=2, color='#2E86AB')
                ax1.axhline(y=goal, color='#E63946', linestyle='--', label='Цель')
                ax1.fill_between(dates, calories, goal, alpha=0.3, color='#E63946')
                ax1.set_title('Калории', fontweight='bold')
                ax1.set_ylabel('ккал')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
            
            # График белков
            if 'protein' in data:
                dates = data['protein']['dates']
                protein = data['protein']['values']
                goal = data['protein'].get('goal', 150)
                
                ax2.plot(dates, protein, marker='s', linewidth=2, color='#06FFA5')
                ax2.axhline(y=goal, color='#FFB700', linestyle='--', label='Цель')
                ax2.set_title('Белки', fontweight='bold')
                ax2.set_ylabel('г')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            
            # График воды
            if 'water' in data:
                dates = data['water']['dates']
                water = data['water']['values']
                goal = data['water'].get('goal', 2000)
                
                ax3.plot(dates, water, marker='^', linewidth=2, color='#4361EE')
                ax3.axhline(y=goal, color='#00D9FF', linestyle='--', label='Цель')
                ax3.fill_between(dates, water, goal, alpha=0.3, color='#00D9FF')
                ax3.set_title('Вода', fontweight='bold')
                ax3.set_ylabel('мл')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            
            # График веса
            if 'weight' in data:
                dates = data['weight']['dates']
                weight = data['weight']['values']
                
                ax4.plot(dates, weight, marker='d', linewidth=2, color='#FF6B6B')
                ax4.set_title('Вес', fontweight='bold')
                ax4.set_ylabel('кг')
                ax4.grid(True, alpha=0.3)
                
                # Добавляем тренд
                if len(weight) > 1:
                    z = np.polyfit(range(len(weight)), weight, 1)
                    p = np.poly1d(z)
                    ax4.plot(dates, p(range(len(weight))), "--", alpha=0.7, color='#4ECDC4')
            
            # Настройка внешнего вида
            plt.tight_layout()
            plt.xticks(rotation=45)
            
            # Конвертация в base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            
            plot_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return plot_data
            
        except Exception as e:
            logger.error(f"Error in sync plot creation: {e}")
            return self._create_error_plot()
    
    def _create_error_plot(self) -> str:
        """Создание заглушки при ошибке"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Ошибка генерации графика', 
                horizontalalignment='center', verticalalignment='center',
                fontsize=16, color='red')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        
        plot_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return plot_data
    
    async def generate_nutrition_pie_chart(self, data: Dict[str, float]) -> str:
        """Генерация круговой диаграммы питания"""
        loop = asyncio.get_event_loop()
        
        try:
            return await loop.run_in_executor(
                self.executor,
                self._create_pie_chart_sync,
                data
            )
        except Exception as e:
            logger.error(f"Error generating pie chart: {e}")
            return self._create_error_plot()
    
    def _create_pie_chart_sync(self, data: Dict[str, float]) -> str:
        """Синхронное создание круговой диаграммы"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            labels = list(data.keys())
            sizes = list(data.values())
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                             autopct='%1.1f%%', startangle=90)
            
            # Улучшение внешнего вида
            for text in texts:
                text.set_fontsize(12)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
            
            ax.set_title('Распределение БЖУ', fontsize=16, fontweight='bold', pad=20)
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            
            plot_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return plot_data
            
        except Exception as e:
            logger.error(f"Error in pie chart creation: {e}")
            return self._create_error_plot()
    
    async def cleanup(self):
        """Очистка ресурсов"""
        self.executor.shutdown(wait=True)

# Глобальный экземпляр
plot_generator = AsyncPlotGenerator()
