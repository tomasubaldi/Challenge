from process import Process

def task():
    """Point of entry for oue Digital Workers process"""
    process = Process()
    try:
        process.start()
    except Exception as error:
        print("An excpetion has occurred!")
        print(f"Exception: {error}")
    finally:
        process.finish()


if __name__ == "__main__":
    task()



