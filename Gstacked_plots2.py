import pandas as pd
import glob
import plotly.express as px
import os

def load_bracken_files(input_folder, rank="G", top_n=15):
    """
    Load and combine Bracken report files from a specified folder, filter by taxonomic level (rank), 
    and keep top N taxa.
    
    Args:
    - input_folder (str): Path to the folder containing Bracken report files.
    - rank (str): The taxonomic level to filter (e.g., 'G' for genus, 'S' for species).
    - top_n (int): Number of top taxa to retain based on overall abundance.
    
    Returns:
    - pd.DataFrame: A DataFrame ready for stacked bar plot visualization.
    """
    file_paths = glob.glob(os.path.join(input_folder, "*.txt"))
    dataframes = []

    # Load each Bracken report file
    for file in file_paths:
        sample_id = os.path.basename(file).replace("_bracken.txt", "")
        df = pd.read_csv(file, sep="\t", usecols=["name", "taxonomy_lvl", "fraction_total_reads"])
        df["sample_id"] = sample_id
        dataframes.append(df)

    # Combine all data into a single DataFrame
    combined_df = pd.concat(dataframes)

    # Filter for the specified taxonomic level (rank)
    filtered_df = combined_df[combined_df["taxonomy_lvl"] == rank]

    if filtered_df.empty:
        print(f"No data found for rank '{rank}'")
        return pd.DataFrame()

    # Find the top N taxa across all samples based on fraction_total_reads
    top_taxa = filtered_df.groupby("name")["fraction_total_reads"].sum().nlargest(top_n).index
    top_taxa_df = filtered_df[filtered_df["name"].isin(top_taxa)]

    return top_taxa_df

def plot_stacked_bar(data, output_file="taxonomic_abundance_stacked_bar.html"):
    """
    Plot a stacked bar chart of taxonomic abundance using plotly and save to file.
    
    Args:
    - data (pd.DataFrame): The data ready for stacked bar plotting.
    - output_file (str): Path to save the generated plot.
    """
    if data.empty:
        print("No data available to plot.")
        return
    
    # Define a custom color sequence or use a predefined one
    color_palette = px.colors.qualitative.Pastel  # You can choose 'Vivid', 'Pastel', 'Dark2', etc.

    # Get unique taxa names
    taxa_names = data['name'].unique()
    
    # Dynamically assign colors by cycling through the chosen palette
    color_map = {taxa: color_palette[i % len(color_palette)] for i, taxa in enumerate(taxa_names)}

    # Plot with the automatically mapped colors
    fig = px.bar(data, 
                 x="sample_id", 
                 y="fraction_total_reads", 
                 color="name",
                 color_discrete_map=color_map,
                 labels={"fraction_total_reads": "Relative Abundance", "sample_id": "Sample ID", "name": "Taxon"},
                 title="Taxonomic Abundance Stacked Bar Plot Across Samples")
    fig.update_layout(barmode='stack', xaxis_tickangle=-45)
    fig.write_html(output_file)
    fig.show()
    print(f"Stacked bar plot saved to {output_file}")

if __name__ == "__main__":
    input_folder = "/home/viroicbas/scriptTeste/bracken_reports"
    output_file = "taxonomic_abundance_stacked_bar.html"

    # Load data and generate stacked bar plot
    bar_data = load_bracken_files(input_folder, rank="G", top_n=15)
    plot_stacked_bar(bar_data, output_file)
