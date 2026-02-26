"""Quick script to construct the command to run the multiviews system."""

from argparse import ArgumentParser


def _construct_command(pod_amount: int, script_path: str, start_port: int) -> str:
    command = f"python3 {script_path} -p "
    command += " ".join(
        [f"http://localhost:{i}/" for i in range(start_port, start_port + pod_amount)]
    )
    return command


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Constructs the command to run the multiviews system."
    )
    parser.add_argument(
        "pod_amount",
        type=int,
        help="The number of pods to include in the multiviews system.",
    )
    parser.add_argument(
        "script_path",
        type=str,
        help="The path to the script to run the multiviews system.",
    )
    parser.add_argument(
        "start_port",
        type=int,
        help="The starting port number for the pods (default: 8000).",
        default=3000,
    )
    args = parser.parse_args()

    print(_construct_command(args.pod_amount, args.script_path, args.start_port))
