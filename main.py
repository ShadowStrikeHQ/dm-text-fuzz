import argparse
import logging
import random
import string
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def setup_argparse():
    """Sets up the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Fuzzes text files by introducing random character substitutions, insertions, and deletions."
    )
    parser.add_argument(
        "input_file", type=Path, help="Path to the input text file."
    )
    parser.add_argument(
        "output_file",
        type=Path,
        help="Path to the output text file.",
    )
    parser.add_argument(
        "--substitution_freq",
        type=float,
        default=0.1,
        help="Frequency of character substitutions (0.0-1.0).",
    )
    parser.add_argument(
        "--insertion_freq",
        type=float,
        default=0.05,
        help="Frequency of character insertions (0.0-1.0).",
    )
    parser.add_argument(
        "--deletion_freq",
        type=float,
        default=0.05,
        help="Frequency of character deletions (0.0-1.0).",
    )
    parser.add_argument(
        "--preserve_punctuation",
        action="store_true",
        help="Preserve punctuation marks during fuzzing.",
    )
    return parser


def fuzz_text(text, sub_freq, ins_freq, del_freq, preserve_punctuation):
    """Fuzzes the input text based on the specified frequencies and settings."""
    fuzzed_text = ""
    for char in text:
        if preserve_punctuation and char in string.punctuation:
            fuzzed_text += char
            continue

        rand_val = random.random()
        if rand_val < sub_freq:  # Substitute a character
            fuzzed_text += random.choice(string.ascii_letters + string.digits)
        elif rand_val < sub_freq + ins_freq:  # Insert a character
            fuzzed_text += random.choice(string.ascii_letters + string.digits) + char
        elif rand_val < sub_freq + ins_freq + del_freq:  # Delete a character
            continue  # Do not add the current character, effectively deleting it
        else:
            fuzzed_text += char
    return fuzzed_text


def validate_args(args):
    """Validates the command-line arguments."""
    if not 0 <= args.substitution_freq <= 1:
        raise ValueError("Substitution frequency must be between 0 and 1.")
    if not 0 <= args.insertion_freq <= 1:
        raise ValueError("Insertion frequency must be between 0 and 1.")
    if not 0 <= args.deletion_freq <= 1:
        raise ValueError("Deletion frequency must be between 0 and 1.")
    if (
        args.substitution_freq + args.insertion_freq + args.deletion_freq
        > 1
    ):  # Checking for a valid probability range
        raise ValueError(
            "Total modification probability cannot be greater than 1."
        )
    if not args.input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")
    if args.output_file.is_dir():
        raise IsADirectoryError(
            f"Output file cannot be a directory: {args.output_file}"
        )


def main():
    """Main function to execute the text fuzzing process."""
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        validate_args(args)
        logging.info(f"Fuzzing file: {args.input_file}")

        with open(args.input_file, "r", encoding="utf-8") as infile:
            text = infile.read()

        fuzzed_text = fuzz_text(
            text,
            args.substitution_freq,
            args.insertion_freq,
            args.deletion_freq,
            args.preserve_punctuation,
        )
        with open(args.output_file, "w", encoding="utf-8") as outfile:
            outfile.write(fuzzed_text)
        logging.info(f"Fuzzed text saved to: {args.output_file}")

    except (
        FileNotFoundError,
        ValueError,
        IsADirectoryError,
        IOError,
    ) as e:
        logging.error(f"Error: {e}")
        sys.exit(1)

    except Exception as e:
        logging.exception("An unexpected error occurred:")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Usage Examples:
# 1. Basic Fuzzing:
#    python dm_text_fuzz.py input.txt output.txt
# 2. Custom Frequencies:
#    python dm_text_fuzz.py input.txt output.txt --substitution_freq 0.2 --insertion_freq 0.1 --deletion_freq 0.1
# 3. Preserve Punctuation:
#    python dm_text_fuzz.py input.txt output.txt --preserve_punctuation
# 4. Full Customization:
#    python dm_text_fuzz.py input.txt output.txt --substitution_freq 0.3 --insertion_freq 0.2 --deletion_freq 0.1 --preserve_punctuation