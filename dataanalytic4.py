# ================================================================
# TASK 4: DATA CLEANING & REPORTING AUTOMATION
# ================================================================
# Features:
#   ✓ CSV / Excel file upload
#   ✓ Automatic data profiling
#   ✓ Missing-value handling
#   ✓ Duplicate removal
#   ✓ Text inconsistency cleaning
#   ✓ Numeric conversion
#   ✓ Automated visual reports
#   ✓ Before/after cleaning statistics
#   ✓ Download cleaned dataset
#   ✓ Download automated CSV report
# ================================================================

import io
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


# ----------------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------------

st.set_page_config(
    page_title="Data Cleaning & Reporting Automation",
    page_icon="🧹",
    layout="wide"
)


# ----------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #64748B;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 25px;
    }

    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 12px;
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ----------------------------------------------------------------
# TITLE
# ----------------------------------------------------------------

st.markdown(
    '<div class="main-title">🧹 Data Cleaning & Reporting Automation</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Automate data preprocessing, quality checks, analysis and reporting'
    '</div>',
    unsafe_allow_html=True
)


# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------

st.sidebar.header("⚙️ Automation Settings")

uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset",
    type=["csv", "xlsx", "xls"]
)

missing_method = st.sidebar.selectbox(
    "Missing Value Strategy",
    [
        "Automatic",
        "Drop Rows",
        "Fill Numeric with Median",
        "Fill All with Mode"
    ]
)

remove_duplicates = st.sidebar.checkbox(
    "Remove Duplicate Rows",
    value=True
)

clean_text = st.sidebar.checkbox(
    "Standardize Text Values",
    value=True
)


# ----------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------

def load_dataset(file):
    """Load CSV or Excel file."""

    extension = file.name.lower().split(".")[-1]

    if extension == "csv":
        return pd.read_csv(file)

    if extension in ["xlsx", "xls"]:
        return pd.read_excel(file)

    raise ValueError("Unsupported file format.")


def clean_column_names(df):
    """Standardize column names."""

    cleaned = []

    for column in df.columns:

        name = str(column).strip()

        name = re.sub(
            r"\s+",
            "_",
            name
        )

        name = re.sub(
            r"[^A-Za-z0-9_]",
            "",
            name
        )

        cleaned.append(name)

    df.columns = cleaned

    return df


def standardize_text_columns(df):
    """Clean inconsistent text formatting."""

    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
        )

        # Convert empty strings to missing values
        df[column] = df[column].replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
                "NULL": pd.NA,
                "null": pd.NA
            }
        )

    return df


def handle_missing_values(df, method):
    """Handle missing values according to selected strategy."""

    if method == "Drop Rows":

        return df.dropna()

    if method == "Fill Numeric with Median":

        for column in df.select_dtypes(
            include=np.number
        ).columns:

            median = df[column].median()

            df[column] = df[column].fillna(
                median
            )

        return df

    if method == "Fill All with Mode":

        for column in df.columns:

            if df[column].isna().any():

                mode = df[column].mode(
                    dropna=True
                )

                if not mode.empty:
                    df[column] = df[column].fillna(
                        mode.iloc[0]
                    )

        return df

    # Automatic strategy
    for column in df.columns:

        if df[column].isna().any():

            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                df[column] = df[column].fillna(
                    df[column].median()
                )

            else:

                mode = df[column].mode(
                    dropna=True
                )

                if not mode.empty:
                    df[column] = df[column].fillna(
                        mode.iloc[0]
                    )

    return df


def create_quality_report(before, after):
    """Create automated data quality report."""

    report = []

    for column in before.columns:

        before_missing = int(
            before[column].isna().sum()
        )

        after_missing = int(
            after[column].isna().sum()
        )

        report.append(
            {
                "Column": column,
                "Data Type": str(
                    after[column].dtype
                ),
                "Missing Before": before_missing,
                "Missing After": after_missing,
                "Unique Values": int(
                    after[column].nunique(
                        dropna=True
                    )
                )
            }
        )

    return pd.DataFrame(report)


# ----------------------------------------------------------------
# DEMO DATA
# ----------------------------------------------------------------

def create_demo_dataset():

    np.random.seed(42)

    size = 150

    data = pd.DataFrame(
        {
            "Customer": [
                f"Customer {i}"
                for i in range(1, size + 1)
            ],

            "Region": np.random.choice(
                [
                    "Hyderabad",
                    " hyderabad ",
                    "Bangalore",
                    "Bengaluru",
                    "Chennai",
                    "chennai"
                ],
                size=size
            ),

            "Sales": np.random.normal(
                5000,
                1200,
                size
            ).round(2),

            "Orders": np.random.randint(
                1,
                15,
                size=size
            ),

            "Category": np.random.choice(
                [
                    "Electronics",
                    "electronics",
                    "Clothing",
                    " clothing ",
                    "Grocery"
                ],
                size=size
            )
        }
    )

    # Add missing values
    data.loc[
        np.random.choice(size, 8),
        "Sales"
    ] = np.nan

    data.loc[
        np.random.choice(size, 5),
        "Region"
    ] = np.nan

    # Add duplicates
    data = pd.concat(
        [
            data,
            data.iloc[:5]
        ],
        ignore_index=True
    )

    return data


# ----------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------

if uploaded_file is not None:

    try:

        original_df = load_dataset(
            uploaded_file
        )

        st.success(
            f"✅ Successfully loaded: {uploaded_file.name}"
        )

    except Exception as error:

        st.error(
            f"❌ Could not read the file: {error}"
        )

        st.stop()

else:

    original_df = create_demo_dataset()

    st.info(
        "ℹ️ No dataset uploaded. A demonstration dataset "
        "is being used. Upload your own CSV/Excel file "
        "from the sidebar."
    )


# Keep original copy
before_df = original_df.copy()

# Clean column names
df = clean_column_names(
    original_df.copy()
)


# ----------------------------------------------------------------
# BEFORE CLEANING SUMMARY
# ----------------------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Dataset Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Rows",
        before_df.shape[0]
    )

with col2:

    st.metric(
        "Columns",
        before_df.shape[1]
    )

with col3:

    st.metric(
        "Missing Values",
        int(
            before_df.isna().sum().sum()
        )
    )

with col4:

    st.metric(
        "Duplicate Rows",
        int(
            before_df.duplicated().sum()
        )
    )


# ----------------------------------------------------------------
# RAW DATA
# ----------------------------------------------------------------

with st.expander(
    "👀 View Raw Dataset"
):

    st.dataframe(
        before_df,
        use_container_width=True
    )


# ----------------------------------------------------------------
# DATA CLEANING
# ----------------------------------------------------------------

with st.spinner(
    "Cleaning and preprocessing data..."
):

    # Standardize text
    if clean_text:

        df = standardize_text_columns(
            df
        )

    # Remove duplicate records
    duplicates_removed = 0

    if remove_duplicates:

        duplicates_removed = int(
            df.duplicated().sum()
        )

        df = df.drop_duplicates()

    # Handle missing values
    missing_before = int(
        df.isna().sum().sum()
    )

    df = handle_missing_values(
        df,
        missing_method
    )

    missing_after = int(
        df.isna().sum().sum()
    )


# ----------------------------------------------------------------
# CLEANING RESULTS
# ----------------------------------------------------------------

st.markdown(
    '<div class="section-title">✨ Cleaning Results</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Original Rows",
        before_df.shape[0]
    )

with col2:

    st.metric(
        "Clean Rows",
        df.shape[0]
    )

with col3:

    st.metric(
        "Duplicates Removed",
        duplicates_removed
    )

with col4:

    st.metric(
        "Missing Remaining",
        missing_after
    )


# ----------------------------------------------------------------
# CLEANED DATA
# ----------------------------------------------------------------

with st.expander(
    "🔍 View Cleaned Dataset",
    expanded=True
):

    st.dataframe(
        df.head(20),
        use_container_width=True
    )


# ----------------------------------------------------------------
# QUALITY REPORT
# ----------------------------------------------------------------

st.markdown(
    '<div class="section-title">📋 Automated Data Quality Report</div>',
    unsafe_allow_html=True
)

quality_report = create_quality_report(
    before_df,
    df
)

st.dataframe(
    quality_report,
    use_container_width=True
)


# ----------------------------------------------------------------
# MISSING VALUE REPORT
# ----------------------------------------------------------------

st.markdown(
    '<div class="section-title">🕵️ Missing Value Analysis</div>',
    unsafe_allow_html=True
)

missing_report = pd.DataFrame(
    {
        "Column": before_df.columns,
        "Missing Values": [
            before_df[column].isna().sum()
            for column in before_df.columns
        ]
    }
)

missing_report = missing_report[
    missing_report["Missing Values"] > 0
]


if missing_report.empty:

    st.success(
        "✅ No missing values detected."
    )

else:

    fig_missing = px.bar(
        missing_report,
        x="Column",
        y="Missing Values",
        title="Missing Values by Column",
        text_auto=True
    )

    fig_missing.update_layout(
        xaxis_title="Column",
        yaxis_title="Missing Values"
    )

    st.plotly_chart(
        fig_missing,
        use_container_width=True
    )


# ----------------------------------------------------------------
# NUMERICAL ANALYSIS
# ----------------------------------------------------------------

numeric_columns = df.select_dtypes(
    include=np.number
).columns.tolist()


if numeric_columns:

    st.markdown(
        '<div class="section-title">📈 Numerical Data Analysis</div>',
        unsafe_allow_html=True
    )

    selected_numeric = st.selectbox(
        "Select Numerical Column",
        numeric_columns
    )

    selected_data = df[
        selected_numeric
    ].dropna()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Average",
            f"{selected_data.mean():,.2f}"
        )

    with col2:

        st.metric(
            "Median",
            f"{selected_data.median():,.2f}"
        )

    with col3:

        st.metric(
            "Minimum",
            f"{selected_data.min():,.2f}"
        )

    with col4:

        st.metric(
            "Maximum",
            f"{selected_data.max():,.2f}"
        )

    # Histogram
    fig_hist = px.histogram(
        df,
        x=selected_numeric,
        title=f"Distribution of {selected_numeric}",
        marginal="box"
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )


# ----------------------------------------------------------------
# CATEGORICAL ANALYSIS
# ----------------------------------------------------------------

categorical_columns = df.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()


if categorical_columns:

    st.markdown(
        '<div class="section-title">📊 Categorical Analysis</div>',
        unsafe_allow_html=True
    )

    selected_category = st.selectbox(
        "Select Categorical Column",
        categorical_columns
    )

    category_counts = (
        df[selected_category]
        .value_counts()
        .reset_index()
    )

    category_counts.columns = [
        selected_category,
        "Count"
    ]

    fig_category = px.bar(
        category_counts.head(15),
        x=selected_category,
        y="Count",
        title=f"Top Categories in {selected_category}",
        text_auto=True
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ----------------------------------------------------------------
# CORRELATION ANALYSIS
# ----------------------------------------------------------------

if len(numeric_columns) >= 2:

    st.markdown(
        '<div class="section-title">🔗 Correlation Analysis</div>',
        unsafe_allow_html=True
    )

    correlation = df[
        numeric_columns
    ].corr()

    fig_corr = px.imshow(
        correlation,
        text_auto=True,
        title="Numerical Feature Correlation",
        aspect="auto"
    )

    st.plotly_chart(
        fig_corr,
        use_container_width=True
    )


# ----------------------------------------------------------------
# AUTOMATED SUMMARY
# ----------------------------------------------------------------

st.markdown(
    '<div class="section-title">📝 Automated Report Summary</div>',
    unsafe_allow_html=True
)

original_rows = before_df.shape[0]
clean_rows = df.shape[0]

rows_removed = (
    original_rows - clean_rows
)

st.write(
    f"""
    **Data Processing Summary**

    - Original dataset contained **{original_rows:,} rows**
      and **{before_df.shape[1]:,} columns**.
    - **{duplicates_removed:,} duplicate rows** were removed.
    - Missing values before cleaning: **{missing_before:,}**.
    - Missing values after cleaning: **{missing_after:,}**.
    - Total rows removed during processing:
      **{rows_removed:,}**.
    - Final dataset contains **{clean_rows:,} clean rows**.
    - The cleaned dataset is ready for further analysis,
      visualization or machine-learning workflows.
    """
)


# ----------------------------------------------------------------
# DOWNLOAD CLEANED DATA
# ----------------------------------------------------------------

st.markdown(
    '<div class="section-title">⬇️ Export Results</div>',
    unsafe_allow_html=True
)


cleaned_csv = df.to_csv(
    index=False
).encode("utf-8")


report_csv = quality_report.to_csv(
    index=False
).encode("utf-8")


col1, col2 = st.columns(2)

with col1:

    st.download_button(
        label="⬇️ Download Cleaned Dataset",
        data=cleaned_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        use_container_width=True
    )


with col2:

    st.download_button(
        label="📄 Download Quality Report",
        data=report_csv,
        file_name="data_quality_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# ----------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------

st.markdown("---")

st.caption(
    "Data Cleaning & Reporting Automation | "
    "Python • Pandas • Streamlit • Plotly"
)