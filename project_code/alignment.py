from Bio.Blast import NCBIWWW, NCBIXML
import time
from datetime import timedelta

# Example input for debugging: MVLSPADKTNVKAAW
print("\n\n-------------------------------------------------")
sequence = input("Enter the sequence to search for: ")
constraint = input("Enter the constraint that should be present: ")


if constraint not in sequence:
    print("The provided constraint is not in the sequence given, try again")
    exit()

try:
    print("\n\nPerforming Blast search. This may take time")
    start = time.time()
    query_result = NCBIWWW.qblast("blastp", "nr", sequence)

    parsed_result = list(NCBIXML.parse(query_result))

    total = time.time() - start
    total = str(timedelta(seconds=total))
    print(f"\nQuery complete in {total}\n")


    for record in parsed_result:
        if not record.alignments:
            print("No alignment found")
            exit()
        high_score = 0
        best_alignment = ""
        for i, alignment in enumerate(record.alignments[:3], start=1):
            for hsp in alignment.hsps:
                if hsp.score > high_score:
                    high_score = hsp.score
                    best_alignment = alignment
                    


    print(f"The best alignment was {best_alignment}, with score {high_score}")

except Exception as exception:
    print("Error during BLAST search:", exception)