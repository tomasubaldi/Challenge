from execution import Execution

def main():
    """Main execution"""
    execution = Execution()
    try:
        execution.start()
    except Exception as error:
        print("An exception has occurred!")
        print(f"Exception: {error}")
    finally:
        execution.finish()

if __name__ == "__main__":
    main()
