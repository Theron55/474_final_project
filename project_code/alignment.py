from Bio.Blast import NCBIWWW, NCBIXML
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import timedelta


# Use this: AGAVALQALKGSQDSSENDLVRSPKSA
# With this constraint: END
"""Still work in progress, instead of composite scoring we can use other algorithms to rank further."""

# Combined Line and Scatter Plot Function
def combined_line_scatter_plot(df, title):
    """
    Create a combined line and scatter plot for BLAST results.
    - Line: Represents Scores.
    - Scatter: Represents E-values (log scale).
    """
    compressed_titles = df["Title"].apply(lambda x: x.split(" ")[0] + "...")
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Line Plot for Scores
    ax1.plot(compressed_titles, df["Score"], color="blue", marker="o", label="Score")
    ax1.set_ylabel("Score", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.set_xticks(range(len(compressed_titles)))
    ax1.set_xticklabels(compressed_titles, rotation=45, ha="right")

    # Scatter Plot for E-values
    ax2 = ax1.twinx()
    ax2.scatter(compressed_titles, df["E-value"], color="red", label="E-value")
    ax2.set_ylabel("E-value (log scale)", color="red")
    ax2.set_yscale("log")
    ax2.tick_params(axis="y", labelcolor="red")

    plt.title(title)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
    plt.tight_layout()
    plt.show()

# Composite Scoring Function
def compute_composite_score(df, weights=(1.0, 1.0, 1.0)):
    """
    Compute composite scores for alignments based on E-value, Percent Identity, and Score.
    """
    w1, w2, w3 = weights
    df["Composite Score"] = (
        w1 * (1 / df["E-value"]) +
        w2 * df["Percent Identity"] +
        w3 * df["Score"]
    )
    return df.sort_values(by="Composite Score", ascending=False)

# BLAST Search and Results Processing
def blast_search(sequence, constraint):
    """
    Perform BLAST search with NCBIWWW and process results.
    """
    if len(sequence) < 25:
        print("Error: Sequence must be at least 25 amino acids long.")
        return None

    if constraint not in sequence:
        print(f"Error: The constraint '{constraint}' is not present in the sequence.")
        return None

    print("\nPerforming BLAST search. This may take some time...")
    alignments_data = []

    try:
        # Start timer
        start = time.time()
        result_handle = NCBIWWW.qblast("blastp", "nr", sequence)

        # Parse BLAST results
        blast_records = list(NCBIXML.parse(result_handle))

        # Measure elapsed time
        elapsed_time = str(timedelta(seconds=(time.time() - start)))
        print(f"\nQuery completed in {elapsed_time}\n")

        for record in blast_records:
            if not record.alignments:
                print("No alignment found.")
                return None

            for alignment in record.alignments[:20]:  # Top 20 alignments
                
                for hsp in alignment.hsps:
                    aligned_sequence = hsp.sbjct.replace("-", " ")
                    if constraint in aligned_sequence:
                        alignments_data.append([
                            alignment.title,
                            hsp.score,
                            hsp.expect,
                            (hsp.identities / hsp.align_length) * 100
                        ])

        # Save results to CSV
        if alignments_data:
            df = pd.DataFrame(alignments_data, columns=["Title", "Score", "E-value", "Percent Identity"])
            df.to_csv("results.csv", index=False)
            print("\nSaved top 20 results to 'results.csv'.")
            return df
        else:
            print("No significant alignments found.")
            return None

    except Exception as e:
        print("Error during BLAST search:", e)
        return None

# Main Workflow
sequence = input("Enter a single sequence (minimum 25 amino acids): ").strip()
constraint = input("Enter a motif (constraint) present in the sequence: ").strip()
   

# Run BLAST search and save top 20 results
top_20_df = blast_search(sequence, constraint)

# Rank results by composite score and save
if top_20_df is not None:
    ranked_df = compute_composite_score(top_20_df)
    ranked_df.to_csv("ranked_results.csv", index=False)
    print("\nSaved ranked results to 'ranked_results.csv'.")

    # Plot top 20 and ranked results
    combined_line_scatter_plot(top_20_df, "Top 20 BLAST Results")
    combined_line_scatter_plot(ranked_df, "Top 5 Ranked BLAST Results")