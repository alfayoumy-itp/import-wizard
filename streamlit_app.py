import streamlit as st
import pandas as pd
import openpyxl

# Upload Templates
TEMPLATES = {
    "Assembly Template": "Assembly Template.xlsx",
    "Bill of Material Template": "Bill of material template.xlsx",
    "Customer Template": "Customer Template.xlsx",
    # Add all templates you have in the dictionary
}

st.title("Interactive Import Wizard")

# Step 1: File Upload
uploaded_file = st.file_uploader("Upload an Excel/CSV File", type=["csv", "xlsx"])

if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == "csv":
        data = pd.read_csv(uploaded_file, dtype=str)
    elif file_extension == "xlsx":
        data = pd.read_excel(uploaded_file, dtype=str)
    
    st.write("Preview of Uploaded File:")
    st.dataframe(data.head())

    # Step 2: Template Selection
    selected_template = st.selectbox("Select the Template", list(TEMPLATES.keys()))
    if selected_template:
        template_file = TEMPLATES[selected_template]
        st.write(f"You selected the `{selected_template}` template.")
        
        # Load template column headers
        try:
            template_data = pd.read_excel(template_file, dtype=str)
            template_columns = template_data.columns.tolist()
        except Exception as e:
            st.error(f"Error loading the template file: {e}")
            template_columns = []

        # Step 3: Mapping Columns
        st.subheader("Column Mapping")
        column_mapping = {}
        for col in template_columns:
            user_column = st.selectbox(
                f"Map `{col}` to your data:",
                options=["--Select--"] + data.columns.tolist(),
                key=col
            )
            if user_column != "--Select--":
                column_mapping[col] = user_column

        # Step 4: Validation and Transformation
        st.subheader("Validation & Transformation")
        for template_col, user_col in column_mapping.items():
            # Example validation: Check if a column contains only numbers
            if template_col in ["Quantity", "Price"]:  # Adjust based on template
                invalid_rows = data[~data[user_col].apply(lambda x: isinstance(x, (int, float)))]
                if not invalid_rows.empty:
                    st.error(f"Invalid data in column `{user_col}`. Please correct.")

        # Step 5: Export
        if st.button("Export Validated File"):
            # Perform transformations if needed
            mapped_data = data.rename(columns=column_mapping)

            # Export to Excel
            output_file = f"Validated_{selected_template}.xlsx"
            mapped_data.to_excel(output_file, index=False)
            
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download File",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
