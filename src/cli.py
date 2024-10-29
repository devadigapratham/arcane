import argparse
from src.trainer import start_training, check_status, stop_training
from src.utils import log_message

def display_ascii_art():
    """Display the ASCII art for Arcane."""
    print(r"""
                                               
    _____ _______   ____ _____    ____   ____      
    \__  \\_  __ \_/ ___\\__  \  /    \_/ __ \     
     / __ \|  | \/\  \___ / __ \|   |  \  ___/     
    (____  /__|    \___  >____  /___|  /\___  > /\ 
         \/            \/     \/     \/     \/  \/ 
    """)

def main():
    display_ascii_art()  # Display the ASCII art at the start

    parser = argparse.ArgumentParser(description="Arcane CLI Tool")
    subparsers = parser.add_subparsers(dest='command')

    # Sub-command for starting training
    train_parser = subparsers.add_parser('train', help='Start a training session')
    train_parser.add_argument('--config', required=True, help='Path to the configuration file')

    # Sub-command for checking status
    subparsers.add_parser('status', help='Check training status')

    # Sub-command for stopping training
    subparsers.add_parser('stop', help='Stop the training session')

    args = parser.parse_args()

    if args.command == 'train':
        start_training(args.config)
    elif args.command == 'status':
        check_status()
    elif args.command == 'stop':
        stop_training()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()