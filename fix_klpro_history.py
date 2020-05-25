#!python
import argparse
import klprotools as klp

def main():
    parser = argparse.ArgumentParser(description="""Tool to fix history files
        created with the 'KlimaLogg Pro' software.""")
    parser.add_argument('input_file', 
                        help='Path to the (corrupted) history file.')
    parser.add_argument('output_file',
                        help="""Path to the (repaired) output file. Note: The
                        file will be overwritten if it already exists!
                        """)
    args = parser.parse_args()
    
    klp.write_file(args.output_file, klp.read_file(args.input_file))

if __name__ == '__main__':
    main()