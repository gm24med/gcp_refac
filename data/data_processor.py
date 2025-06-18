"""Data processing and preparation utilities."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
import logging

class DataProcessor:
    """Handle data loading, processing, and preparation."""
    
    def __init__(self, data_dir: Path, random_seed: int = 42):
        """
        Initialize data processor.
        
        Args:
            data_dir: Directory containing data files
            random_seed: Random seed for reproducibility
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.random_seed = random_seed
        
        # Get a standard logger for this module
        self._logger = logging.getLogger(__name__)
    
    def load_dataset(
        self,
        filename: str,
        text_column: str = 'Text',
        label_column: str = 'Label',
        id_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load dataset from file.
        
        Args:
            filename: Name of the data file
            text_column: Name of the text column
            label_column: Name of the label column
            id_column: Optional ID column name
            
        Returns:
            Loaded DataFrame
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        # Load based on file extension
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Use .csv or .xlsx")
        
        # Validate required columns
        required_cols = [text_column, label_column]
        if id_column:
            required_cols.append(id_column)
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return df
    
    def create_balanced_dataset(
        self,
        df: pd.DataFrame,
        label_column: str = 'Label',
        max_samples: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Create a balanced dataset by undersampling majority classes.
        
        Args:
            df: Input DataFrame
            label_column: Name of the label column
            max_samples: Maximum number of samples per class
            
        Returns:
            Balanced DataFrame
        """
        self._logger.info("Creating balanced dataset...")
        class_counts = df[label_column].value_counts()
        
        min_samples = class_counts.min()
        if max_samples and max_samples < min_samples * len(class_counts):
            samples_per_class = int(max_samples / len(class_counts))
            self._logger.info(f"Using {samples_per_class} samples per class (from max_samples={max_samples})")
        else:
            samples_per_class = min_samples
            self._logger.info(f"Using {samples_per_class} samples per class (min class size)")
        
        balanced_df = pd.DataFrame()
        for label in class_counts.index:
            class_df = df[df[label_column] == label]
            if len(class_df) > samples_per_class:
                class_df = class_df.sample(n=samples_per_class, random_state=self.random_seed)
            balanced_df = pd.concat([balanced_df, class_df])
        
        # Shuffle the final dataframe
        balanced_df = balanced_df.sample(frac=1, random_state=self.random_seed).reset_index(drop=True)
        
        self._logger.info(f"Created balanced dataset with {len(balanced_df)} examples")
        return balanced_df
    
    def split_dataset(
        self,
        df: pd.DataFrame,
        label_column: str = 'Label',
        test_size: float = 0.2,
        val_size: float = 0.1,
        stratify: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split dataset into train, validation, and test sets.
        
        Args:
            df: Input DataFrame
            label_column: Name of the label column
            test_size: Proportion of test set
            val_size: Proportion of validation set
            stratify: Whether to stratify by label
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        from sklearn.model_selection import train_test_split
        
        # Calculate validation size relative to remaining data
        val_ratio = val_size / (1 - test_size)
        
        # First split: separate test set
        stratify_col = df[label_column] if stratify else None
        train_val_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=self.random_seed,
            stratify=stratify_col
        )
        
        # Second split: separate validation set
        stratify_col = train_val_df[label_column] if stratify else None
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=val_ratio,
            random_state=self.random_seed,
            stratify=stratify_col
        )
        
        return train_df, val_df, test_df
    
    def save_dataset(
        self,
        df: pd.DataFrame,
        filename: str,
        format: str = 'csv'
    ) -> None:
        """
        Save dataset to file.
        
        Args:
            df: DataFrame to save
            filename: Output filename
            format: Output format ('csv' or 'xlsx')
        """
        file_path = self.data_dir / filename
        
        if format == 'csv':
            df.to_csv(file_path, index=False)
        elif format == 'xlsx':
            df.to_excel(file_path, index=False)
        else:
            raise ValueError("Unsupported format. Use 'csv' or 'xlsx'")
        
        self._logger.info(f"Dataset saved to {file_path}")