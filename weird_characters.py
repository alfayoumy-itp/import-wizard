import re
import pandas as pd

# Define regex patterns for English and Arabic
ENGLISH_CHARACTERS = re.compile(r'[\x20-\x7E\n]+')
ARABIC_CHARACTERS = re.compile(r'[\x20-\x7E\u0600-\u06FF\u0750-\u077F\n]+')

def remove_weird_characters(s, pattern):
    """
    Remove weird characters from the string, keeping only those defined in the pattern.
    """
    return ''.join(pattern.findall(s))

def clean_columns(df, selected_columns, language):
    """
    Cleans weird characters from the specified columns of a DataFrame.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        selected_columns (list): List of columns to clean.
        language (str): The language for character validation ("English" or "Arabic").

    Returns:
        tuple: (cleaned DataFrame, DataFrame of rows with weird characters)
    """
    # Choose the appropriate regex pattern
    pattern = ENGLISH_CHARACTERS if language == "English" else ARABIC_CHARACTERS
    
    # Create a copy of the DataFrame for cleaning
    cleaned_df = df.copy()
    rows_with_weird_characters = []

    for col in selected_columns:
        # Clean column data
        cleaned_df[col] = cleaned_df[col].apply(
            lambda x: remove_weird_characters(x, pattern) if isinstance(x, str) else x
        )

        # Identify rows with weird characters
        weird_rows = df[df[col] != cleaned_df[col]]
        rows_with_weird_characters.append(weird_rows)

    # Concatenate rows with weird characters into a single DataFrame
    if rows_with_weird_characters:
        weird_characters_df = pd.concat(rows_with_weird_characters).drop_duplicates()
    else:
        weird_characters_df = pd.DataFrame(columns=df.columns)

    return cleaned_df, weird_characters_df
