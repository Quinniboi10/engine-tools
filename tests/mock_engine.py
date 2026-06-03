def main():
    searching = False
    while True:
        command = input().strip()

        if command == "uci":
            print(f"id name Test Engine")
            print(f"id author Engine Tools Author")
            print("uciok", flush=True)
        elif command == "ucinewgame":
            pass
        elif command == "isready":
            print("readyok", flush=True)
        elif command.startswith("go"):
            searching = True
        elif command == "stop":
            searching = False
        elif command == "quit":
            break
    
    raise SystemExit(0 if not searching else 1)

if __name__ == "__main__":
    main()